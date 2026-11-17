"""Camada de repositório: todo o SQL das tabelas carteiras e movimentacoes.

`bloquear_carteira` e `lancar_movimentacao` também são usadas pelos módulos de
compras e de administração, sempre dentro de uma transação já aberta.
"""
from ..conexao import conectar, transacao  # noqa: F401  (transacao é usada pelo service)
from ..erros import ErroNegocio
from ..http import data_utc

COLUNAS_CARTEIRA = "id_carteira, id_usuario, saldo_centavos, atualizado_em"

TAMANHO_DESCRICAO = 200


def _fechar(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def carteira_json(carteira):
    """Objeto "carteira" enviado à tela."""
    if carteira is None:
        return None
    return {
        "id_carteira": carteira["id_carteira"],
        "saldo_centavos": int(carteira["saldo_centavos"]),
        "atualizado_em": data_utc(carteira["atualizado_em"]),
    }


def movimentacao_json(row):
    """Objeto "movimentacao" enviado à tela (valor_centavos tem sinal)."""
    if row is None:
        return None
    return {
        "id_movimentacao": row["id_movimentacao"],
        "tipo": row["tipo"],
        "valor_centavos": int(row["valor_centavos"]),
        "saldo_apos_centavos": int(row["saldo_apos_centavos"]),
        "descricao": row["descricao"],
        "id_compra": row["id_compra"],
        "data_hora": data_utc(row["data_hora"]),
    }


# ---------- consultas com conexão própria ----------

def buscar_carteira(id_usuario):
    """Carteira do usuário (sem bloqueio) ou None se ainda não existir."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {COLUNAS_CARTEIRA} FROM carteiras WHERE id_usuario = %s",
            (id_usuario,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        _fechar(connection, cursor)


def listar_movimentacoes(id_usuario, limite):
    """Extrato do usuário, mais recentes primeiro."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT m.id_movimentacao, m.tipo, m.valor_centavos, m.saldo_apos_centavos,
                      m.descricao, m.id_compra, m.data_hora
               FROM movimentacoes m
               JOIN carteiras c ON c.id_carteira = m.id_carteira
               WHERE c.id_usuario = %s
               ORDER BY m.data_hora DESC, m.id_movimentacao DESC
               LIMIT %s""",
            (id_usuario, limite),
        )
        return [movimentacao_json(row) for row in cursor.fetchall()]
    finally:
        _fechar(connection, cursor)


# ---------- operações dentro de uma transação (recebem o cursor) ----------

def bloquear_carteira(cursor, id_usuario):
    """Trava a carteira do usuário até o fim da transação (SELECT ... FOR UPDATE).

    Enquanto a transação não termina, nenhuma outra requisição altera este saldo.
    Quem ainda não tem carteira (por exemplo, um usuário criado direto no banco)
    ganha uma com saldo zero. Devolve None se o usuário não existir.
    """
    sql = f"SELECT {COLUNAS_CARTEIRA} FROM carteiras WHERE id_usuario = %s FOR UPDATE"
    cursor.execute(sql, (id_usuario,))
    row = cursor.fetchone()
    if row is None:
        # O SELECT só insere se o usuário existir; o IGNORE cobre o caso de outra
        # requisição ter criado a carteira no mesmo instante.
        cursor.execute(
            """INSERT IGNORE INTO carteiras (id_usuario, saldo_centavos)
               SELECT id_usuario, 0 FROM usuarios WHERE id_usuario = %s""",
            (id_usuario,),
        )
        cursor.execute(sql, (id_usuario,))
        row = cursor.fetchone()
    return dict(row) if row else None


def carregar_movimentacao_por_chave(cursor, chave_idempotencia):
    """Movimentação já gravada com esta chave (inclui id_carteira) ou None."""
    cursor.execute(
        """SELECT id_movimentacao, id_carteira, tipo, valor_centavos, saldo_apos_centavos,
                  descricao, id_compra, data_hora
           FROM movimentacoes
           WHERE chave_idempotencia = %s""",
        (chave_idempotencia,),
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def lancar_movimentacao(cursor, carteira, tipo, valor_centavos, descricao, id_autor,
                        id_compra=None, chave_idempotencia=None):
    """Altera o saldo e grava a linha do extrato, tudo na transação do cursor.

    `carteira` é o dicionário devolvido por `bloquear_carteira` (linha já travada)
    e `valor_centavos` tem sinal: positivo soma, negativo desconta. O dicionário
    recebido sai com o saldo novo. Devolve a movimentação no formato da tela.
    """
    saldo_atual = carteira["saldo_centavos"]
    novo_saldo = saldo_atual + valor_centavos
    if novo_saldo < 0:
        raise ErroNegocio(
            "Saldo insuficiente: a operação deixaria a carteira com saldo negativo.",
            codigo="SALDO_INSUFICIENTE",
            detalhes={"saldo_centavos": saldo_atual, "total_centavos": -valor_centavos},
        )

    cursor.execute(
        "UPDATE carteiras SET saldo_centavos = %s WHERE id_carteira = %s",
        (novo_saldo, carteira["id_carteira"]),
    )
    cursor.execute(
        """INSERT INTO movimentacoes
               (id_carteira, tipo, valor_centavos, saldo_apos_centavos, descricao,
                id_compra, id_autor, chave_idempotencia)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            carteira["id_carteira"],
            tipo,
            valor_centavos,
            novo_saldo,
            descricao[:TAMANHO_DESCRICAO],
            id_compra,
            id_autor,
            chave_idempotencia,
        ),
    )
    id_movimentacao = cursor.lastrowid
    # Relê a linha para devolver as datas gravadas pelo banco.
    cursor.execute(
        """SELECT m.id_movimentacao, m.tipo, m.valor_centavos, m.saldo_apos_centavos,
                  m.descricao, m.id_compra, m.data_hora,
                  c.atualizado_em AS carteira_atualizado_em
           FROM movimentacoes m
           JOIN carteiras c ON c.id_carteira = m.id_carteira
           WHERE m.id_movimentacao = %s""",
        (id_movimentacao,),
    )
    row = cursor.fetchone()
    carteira["saldo_centavos"] = novo_saldo
    carteira["atualizado_em"] = row["carteira_atualizado_em"]
    return movimentacao_json(row)
