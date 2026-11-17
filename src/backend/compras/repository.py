"""Camada de repositório: todo o SQL das tabelas compras e itens_compra.

Também faz o bloqueio e a baixa de estoque dos produtos, que só acontecem
dentro da transação da compra.
"""
from ..conexao import conectar, transacao  # noqa: F401  (transacao é usada pelo service)
from ..http import data_utc

COLUNAS_COMPRA = "id_compra, id_usuario, valor_total_centavos, data_hora"


def _fechar(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def compra_json(compra):
    """Objeto "compra" enviado à tela: sem id_usuario, chave nem custo dos itens."""
    if compra is None:
        return None
    return {
        "id_compra": compra["id_compra"],
        "valor_total_centavos": int(compra["valor_total_centavos"]),
        "data_hora": data_utc(compra["data_hora"]),
        "itens": compra["itens"],
    }


def _anexar_itens(cursor, compras):
    """Busca os itens de todas as compras em uma única consulta.

    Evita o problema N+1 (uma consulta de itens para cada compra do histórico).
    """
    por_id = {}
    for compra in compras:
        compra["itens"] = []
        por_id[compra["id_compra"]] = compra
    if not por_id:
        return compras

    marcadores = ", ".join(["%s"] * len(por_id))
    cursor.execute(
        f"""SELECT i.id_compra, i.id_produto, p.nome, i.quantidade,
                   i.preco_unitario_centavos, i.subtotal_centavos
            FROM itens_compra i
            JOIN produtos p ON p.id_produto = i.id_produto
            WHERE i.id_compra IN ({marcadores})
            ORDER BY i.id_compra, i.id_item_compra""",
        tuple(por_id),
    )
    for row in cursor.fetchall():
        por_id[row["id_compra"]]["itens"].append(
            {
                "id_produto": row["id_produto"],
                "nome": row["nome"],
                "quantidade": row["quantidade"],
                "preco_unitario_centavos": row["preco_unitario_centavos"],
                "subtotal_centavos": row["subtotal_centavos"],
            }
        )
    return compras


def _com_itens(cursor, row):
    if row is None:
        return None
    return _anexar_itens(cursor, [dict(row)])[0]


# ---------- consultas com conexão própria ----------

def listar_compras(id_usuario, limite):
    """Compras do usuário com os itens, mais recentes primeiro."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            f"""SELECT {COLUNAS_COMPRA}
                FROM compras
                WHERE id_usuario = %s
                ORDER BY data_hora DESC, id_compra DESC
                LIMIT %s""",
            (id_usuario, limite),
        )
        compras = [dict(row) for row in cursor.fetchall()]
        return _anexar_itens(cursor, compras)
    finally:
        _fechar(connection, cursor)


def consultar_compra(id_compra):
    """Compra com itens (inclui id_usuario, para o service conferir o dono) ou None."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        return carregar_compra(cursor, id_compra)
    finally:
        _fechar(connection, cursor)


# ---------- operações dentro de uma transação (recebem o cursor) ----------

def carregar_compra(cursor, id_compra):
    cursor.execute(
        f"SELECT {COLUNAS_COMPRA} FROM compras WHERE id_compra = %s", (id_compra,)
    )
    return _com_itens(cursor, cursor.fetchone())


def carregar_por_chave(cursor, chave_idempotencia):
    """Compra já gravada com esta chave de idempotência (de qualquer usuário) ou None."""
    cursor.execute(
        f"SELECT {COLUNAS_COMPRA} FROM compras WHERE chave_idempotencia = %s",
        (chave_idempotencia,),
    )
    return _com_itens(cursor, cursor.fetchone())


def bloquear_produtos(cursor, ids_produto):
    """Trava os produtos da compra até o fim da transação, em ordem crescente de id.

    Toda compra trava na mesma ordem (carteira primeiro, depois produtos por id);
    assim duas compras simultâneas nunca ficam uma esperando a outra (deadlock).
    Devolve {id_produto: linha}. Ids que não existem ficam de fora do dicionário.
    """
    ids = sorted(ids_produto)
    if not ids:
        return {}
    marcadores = ", ".join(["%s"] * len(ids))
    cursor.execute(
        f"""SELECT id_produto, nome, preco_compra_centavos, preco_venda_centavos,
                   quantidade_estoque, status
            FROM produtos
            WHERE id_produto IN ({marcadores})
            ORDER BY id_produto
            FOR UPDATE""",
        tuple(ids),
    )
    return {row["id_produto"]: dict(row) for row in cursor.fetchall()}


def inserir_compra(cursor, id_usuario, valor_total_centavos, chave_idempotencia):
    cursor.execute(
        """INSERT INTO compras (id_usuario, valor_total_centavos, chave_idempotencia)
           VALUES (%s, %s, %s)""",
        (id_usuario, valor_total_centavos, chave_idempotencia),
    )
    return cursor.lastrowid


def inserir_itens(cursor, id_compra, linhas):
    """Grava cada item com o preço de venda e o custo do momento da compra."""
    for linha in linhas:
        cursor.execute(
            """INSERT INTO itens_compra
                   (id_compra, id_produto, quantidade, preco_unitario_centavos,
                    custo_unitario_centavos, subtotal_centavos)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                id_compra,
                linha["id_produto"],
                linha["quantidade"],
                linha["preco_unitario_centavos"],
                linha["custo_unitario_centavos"],
                linha["subtotal_centavos"],
            ),
        )


def baixar_estoque(cursor, linhas):
    """Desconta do estoque as quantidades compradas (produtos já travados)."""
    for linha in linhas:
        cursor.execute(
            """UPDATE produtos
               SET quantidade_estoque = quantidade_estoque - %s
               WHERE id_produto = %s""",
            (linha["quantidade"], linha["id_produto"]),
        )
