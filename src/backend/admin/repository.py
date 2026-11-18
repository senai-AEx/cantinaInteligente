"""Camada de repositório da administração: SQL de usuários, movimentações e relatórios.

As colunas `data_hora` estão em UTC. Os períodos chegam aqui já convertidos
para um intervalo UTC (início incluído, fim excluído).
"""
import mysql.connector

from ..conexao import conectar, transacao  # noqa: F401  (transacao é usada pelo service)
from ..http import data_utc
from ..usuarios.repository import usuario_json

SELECT_USUARIO = """SELECT u.id_usuario, u.nome, u.matricula, u.cpf, u.email,
           t.nome AS perfil, u.status,
           COALESCE(c.saldo_centavos, 0) AS saldo_centavos, u.criado_em
    FROM usuarios u
    JOIN tipos_usuario t ON t.id_tipo_usuario = u.id_tipo_usuario
    LEFT JOIN carteiras c ON c.id_usuario = u.id_usuario"""

# Erro do MySQL para valor repetido em coluna única.
ERRNO_DUPLICADO = 1062
RESTRICOES_UNICAS = {
    "uq_usuarios_matricula": "matricula",
    "uq_usuarios_email": "email",
}

# Converte a data UTC do banco para o dia local de Brasília (UTC−3 fixo).
# Offsets numéricos funcionam sem as tabelas de fuso horário do MySQL.
DIA_LOCAL = "DATE(CONVERT_TZ(data_hora, '+00:00', '-03:00'))"


class RegistroDuplicado(Exception):
    """Matrícula ou e-mail já pertence a outro usuário. `campo` diz qual."""

    def __init__(self, campo):
        super().__init__(f"Valor repetido no campo {campo}.")
        self.campo = campo


def _fechar(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def inteiro(valor):
    """SUM() do MySQL devolve Decimal, ou None quando não há linhas."""
    return int(valor) if valor is not None else 0


def padrao_busca(termo):
    """Monta o padrão do LIKE tratando %, _ e \\ digitados como texto comum."""
    for especial in ("\\", "%", "_"):
        termo = termo.replace(especial, "\\" + especial)
    return f"%{termo}%"


def campo_duplicado(mensagem):
    """Descobre o campo repetido pelo nome da restrição na mensagem do erro 1062.

    Exemplo: Duplicate entry 'x@y.com' for key 'usuarios.uq_usuarios_email'
    """
    # Olha só o trecho depois de "for key": o valor repetido vem antes e é
    # texto digitado pelo usuário.
    trecho = str(mensagem or "").rsplit(" for key ", 1)[-1]
    for restricao, campo in RESTRICOES_UNICAS.items():
        if restricao in trecho:
            return campo
    return None


def _movimentacao_json(row):
    return {
        "id_movimentacao": row["id_movimentacao"],
        "tipo": row["tipo"],
        "valor_centavos": row["valor_centavos"],
        "saldo_apos_centavos": row["saldo_apos_centavos"],
        "descricao": row["descricao"],
        "id_compra": row["id_compra"],
        "data_hora": data_utc(row["data_hora"]),
        "usuario": {
            "id_usuario": row["id_usuario"],
            "nome": row["nome"],
            "matricula": row["matricula"],
        },
    }


def _compra_json(row):
    return {
        "id_compra": row["id_compra"],
        "data_hora": data_utc(row["data_hora"]),
        "valor_total_centavos": row["valor_total_centavos"],
        "usuario": {
            "id_usuario": row["id_usuario"],
            "nome": row["nome"],
            "matricula": row["matricula"],
        },
        "itens": [],
    }


def juntar_itens(compras, linhas):
    """Coloca cada linha de `itens_compra` na lista `itens` da sua compra.

    As linhas chegam de uma única consulta para todas as compras da página
    (evita uma consulta por compra) e a ordem delas é mantida.
    """
    itens_por_compra = {compra["id_compra"]: compra["itens"] for compra in compras}
    for row in linhas:
        itens_por_compra[row["id_compra"]].append(
            {
                "id_produto": row["id_produto"],
                "nome": row["nome"],
                "quantidade": row["quantidade"],
                "preco_unitario_centavos": row["preco_unitario_centavos"],
                "subtotal_centavos": row["subtotal_centavos"],
            }
        )
    return compras


# ---------- usuários: consultas com conexão própria ----------

def listar_usuarios(termo, status, perfil):
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        sql = SELECT_USUARIO + " WHERE 1 = 1"
        params = []
        if termo:
            busca = padrao_busca(termo)
            sql += " AND (u.nome LIKE %s OR u.matricula LIKE %s OR u.email LIKE %s)"
            params.extend((busca, busca, busca))
        if status != "TODOS":
            sql += " AND u.status = %s"
            params.append(status)
        if perfil != "TODOS":
            sql += " AND t.nome = %s"
            params.append(perfil)
        sql += " ORDER BY u.nome, u.id_usuario"
        cursor.execute(sql, params)
        return [usuario_json(row) for row in cursor.fetchall()]
    finally:
        _fechar(connection, cursor)


def consultar_usuario(id_usuario):
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        return carregar_usuario(cursor, id_usuario)
    finally:
        _fechar(connection, cursor)


# ---------- usuários: operações dentro de uma transação (recebem o cursor) ----------

def carregar_usuario(cursor, id_usuario, bloquear=False):
    if bloquear:
        # Bloqueia somente a linha do usuário. A carteira fica livre para não
        # disputar com compras e créditos que estejam em andamento.
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE id_usuario = %s FOR UPDATE",
            (id_usuario,),
        )
        if cursor.fetchone() is None:
            return None
    cursor.execute(SELECT_USUARIO + " WHERE u.id_usuario = %s", (id_usuario,))
    row = cursor.fetchone()
    return usuario_json(row) if row is not None else None


def atualizar_usuario(cursor, id_usuario, dados):
    """Grava nome, matrícula, e-mail e perfil. Lança RegistroDuplicado se repetir."""
    try:
        cursor.execute(
            """UPDATE usuarios
               SET nome = %s, matricula = %s, email = %s,
                   id_tipo_usuario = (
                       SELECT id_tipo_usuario FROM tipos_usuario WHERE nome = %s
                   )
               WHERE id_usuario = %s""",
            (dados["nome"], dados["matricula"], dados["email"], dados["perfil"], id_usuario),
        )
    except mysql.connector.Error as exc:
        campo = campo_duplicado(exc) if exc.errno == ERRNO_DUPLICADO else None
        if campo is None:
            raise
        raise RegistroDuplicado(campo) from exc


def atualizar_status(cursor, id_usuario, status):
    cursor.execute(
        "UPDATE usuarios SET status = %s WHERE id_usuario = %s",
        (status, id_usuario),
    )


# ---------- movimentações ----------

def listar_movimentacoes(inicio_utc, fim_utc, tipo, id_usuario, limite):
    """Devolve (movimentações mais recentes primeiro, totais de todo o período filtrado)."""
    # `filtro` é montado apenas com textos fixos; os valores vão em `params`.
    condicoes = ["m.data_hora >= %s", "m.data_hora < %s"]
    params = [inicio_utc, fim_utc]
    if tipo != "TODOS":
        condicoes.append("m.tipo = %s")
        params.append(tipo)
    if id_usuario is not None:
        condicoes.append("c.id_usuario = %s")
        params.append(id_usuario)
    filtro = " AND ".join(condicoes)

    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            f"""SELECT m.id_movimentacao, m.tipo, m.valor_centavos, m.saldo_apos_centavos,
                       m.descricao, m.id_compra, m.data_hora,
                       u.id_usuario, u.nome, u.matricula
                FROM movimentacoes m
                JOIN carteiras c ON c.id_carteira = m.id_carteira
                JOIN usuarios u ON u.id_usuario = c.id_usuario
                WHERE {filtro}
                ORDER BY m.data_hora DESC, m.id_movimentacao DESC
                LIMIT %s""",
            params + [limite],
        )
        movimentacoes = [_movimentacao_json(row) for row in cursor.fetchall()]

        # Os totais não usam LIMIT: somam tudo o que o filtro alcança.
        cursor.execute(
            f"""SELECT
                    SUM(CASE WHEN m.tipo = 'CREDITO' THEN m.valor_centavos ELSE 0 END)
                        AS creditos_centavos,
                    SUM(CASE WHEN m.tipo = 'DEBITO' THEN m.valor_centavos ELSE 0 END)
                        AS debitos_centavos,
                    SUM(CASE WHEN m.tipo = 'AJUSTE' THEN m.valor_centavos ELSE 0 END)
                        AS ajustes_centavos
                FROM movimentacoes m
                JOIN carteiras c ON c.id_carteira = m.id_carteira
                WHERE {filtro}""",
            params,
        )
        row = cursor.fetchone()
        totais = {
            "creditos_centavos": inteiro(row["creditos_centavos"]),
            "debitos_centavos": inteiro(row["debitos_centavos"]),
            "ajustes_centavos": inteiro(row["ajustes_centavos"]),
        }
        return movimentacoes, totais
    finally:
        _fechar(connection, cursor)


# ---------- compras registradas ----------

def listar_compras(inicio_utc, fim_utc, id_usuario, limite):
    """Devolve (compras mais recentes primeiro, com usuário e itens; total do filtro)."""
    # `filtro` é montado apenas com textos fixos; os valores vão em `params`.
    condicoes = ["c.data_hora >= %s", "c.data_hora < %s"]
    params = [inicio_utc, fim_utc]
    if id_usuario is not None:
        condicoes.append("c.id_usuario = %s")
        params.append(id_usuario)
    filtro = " AND ".join(condicoes)

    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)

        # O total não usa LIMIT: conta tudo o que o filtro alcança.
        cursor.execute(
            f"SELECT COUNT(*) AS total_compras FROM compras c WHERE {filtro}", params
        )
        total_compras = inteiro(cursor.fetchone()["total_compras"])

        cursor.execute(
            f"""SELECT c.id_compra, c.data_hora, c.valor_total_centavos,
                       u.id_usuario, u.nome, u.matricula
                FROM compras c
                JOIN usuarios u ON u.id_usuario = c.id_usuario
                WHERE {filtro}
                ORDER BY c.data_hora DESC, c.id_compra DESC
                LIMIT %s""",
            params + [limite],
        )
        compras = [_compra_json(row) for row in cursor.fetchall()]

        if compras:
            # Uma consulta só para os itens de todas as compras da página.
            # `marcadores` é apenas "%s, %s, ..."; os ids vão como parâmetros.
            marcadores = ", ".join(["%s"] * len(compras))
            cursor.execute(
                f"""SELECT i.id_compra, i.id_produto, p.nome, i.quantidade,
                           i.preco_unitario_centavos, i.subtotal_centavos
                    FROM itens_compra i
                    JOIN produtos p ON p.id_produto = i.id_produto
                    WHERE i.id_compra IN ({marcadores})
                    ORDER BY i.id_compra, i.id_item_compra""",
                [compra["id_compra"] for compra in compras],
            )
            juntar_itens(compras, cursor.fetchall())
        return compras, total_compras
    finally:
        _fechar(connection, cursor)


# ---------- relatórios ----------

def relatorio_vendas(inicio_utc, fim_utc):
    """Devolve (totais, por_produto, por_dia, por_usuario) das compras do período."""
    periodo = (inicio_utc, fim_utc)
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """SELECT COUNT(*) AS quantidade_compras,
                      SUM(valor_total_centavos) AS total_centavos
               FROM compras
               WHERE data_hora >= %s AND data_hora < %s""",
            periodo,
        )
        compras = cursor.fetchone()

        # O custo vem do item: é o preço de compra guardado no momento da venda.
        cursor.execute(
            """SELECT SUM(i.quantidade) AS itens_vendidos,
                      SUM(i.quantidade * i.custo_unitario_centavos) AS custo_centavos
               FROM itens_compra i
               JOIN compras c ON c.id_compra = i.id_compra
               WHERE c.data_hora >= %s AND c.data_hora < %s""",
            periodo,
        )
        itens = cursor.fetchone()
        totais = {
            "quantidade_compras": inteiro(compras["quantidade_compras"]),
            "itens_vendidos": inteiro(itens["itens_vendidos"]),
            "total_centavos": inteiro(compras["total_centavos"]),
            "custo_centavos": inteiro(itens["custo_centavos"]),
        }

        cursor.execute(
            """SELECT i.id_produto, p.nome, p.categoria,
                      SUM(i.quantidade) AS quantidade,
                      SUM(i.subtotal_centavos) AS total_centavos,
                      SUM(i.subtotal_centavos - i.quantidade * i.custo_unitario_centavos)
                          AS lucro_centavos
               FROM itens_compra i
               JOIN compras c ON c.id_compra = i.id_compra
               JOIN produtos p ON p.id_produto = i.id_produto
               WHERE c.data_hora >= %s AND c.data_hora < %s
               GROUP BY i.id_produto, p.nome, p.categoria
               ORDER BY total_centavos DESC, p.nome, i.id_produto""",
            periodo,
        )
        por_produto = [
            {
                "id_produto": row["id_produto"],
                "nome": row["nome"],
                "categoria": row["categoria"],
                "quantidade": inteiro(row["quantidade"]),
                "total_centavos": inteiro(row["total_centavos"]),
                "lucro_centavos": inteiro(row["lucro_centavos"]),
            }
            for row in cursor.fetchall()
        ]

        cursor.execute(
            f"""SELECT {DIA_LOCAL} AS dia,
                       COUNT(*) AS quantidade_compras,
                       SUM(valor_total_centavos) AS total_centavos
                FROM compras
                WHERE data_hora >= %s AND data_hora < %s
                GROUP BY dia
                ORDER BY dia""",
            periodo,
        )
        por_dia = [
            {
                "data": data_utc(row["dia"]),
                "quantidade_compras": inteiro(row["quantidade_compras"]),
                "total_centavos": inteiro(row["total_centavos"]),
            }
            for row in cursor.fetchall()
        ]

        # Consumo por usuário. Compras e itens são somados em subconsultas
        # separadas: juntar `compras` direto com `itens_compra` repetiria o
        # valor da compra uma vez para cada item dela.
        cursor.execute(
            """SELECT u.id_usuario, u.nome, u.matricula,
                      tc.quantidade_compras, COALESCE(ti.itens, 0) AS itens,
                      tc.total_centavos
               FROM (
                   SELECT id_usuario, COUNT(*) AS quantidade_compras,
                          SUM(valor_total_centavos) AS total_centavos
                   FROM compras
                   WHERE data_hora >= %s AND data_hora < %s
                   GROUP BY id_usuario
               ) tc
               JOIN usuarios u ON u.id_usuario = tc.id_usuario
               LEFT JOIN (
                   SELECT c.id_usuario, SUM(i.quantidade) AS itens
                   FROM itens_compra i
                   JOIN compras c ON c.id_compra = i.id_compra
                   WHERE c.data_hora >= %s AND c.data_hora < %s
                   GROUP BY c.id_usuario
               ) ti ON ti.id_usuario = tc.id_usuario
               ORDER BY tc.total_centavos DESC, u.nome, u.id_usuario""",
            periodo + periodo,
        )
        por_usuario = [
            {
                "id_usuario": row["id_usuario"],
                "nome": row["nome"],
                "matricula": row["matricula"],
                "quantidade_compras": inteiro(row["quantidade_compras"]),
                "itens": inteiro(row["itens"]),
                "total_centavos": inteiro(row["total_centavos"]),
            }
            for row in cursor.fetchall()
        ]
        return totais, por_produto, por_dia, por_usuario
    finally:
        _fechar(connection, cursor)


def listar_saldos(perfil):
    """Usuários do perfil informado, do maior para o menor saldo."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT u.id_usuario, u.nome, u.matricula, u.status,
                      COALESCE(c.saldo_centavos, 0) AS saldo_centavos
               FROM usuarios u
               JOIN tipos_usuario t ON t.id_tipo_usuario = u.id_tipo_usuario
               LEFT JOIN carteiras c ON c.id_usuario = u.id_usuario
               WHERE t.nome = %s
               ORDER BY COALESCE(c.saldo_centavos, 0) DESC, u.nome, u.id_usuario""",
            (perfil,),
        )
        return [
            {
                "id_usuario": row["id_usuario"],
                "nome": row["nome"],
                "matricula": row["matricula"],
                "status": row["status"],
                "saldo_centavos": inteiro(row["saldo_centavos"]),
            }
            for row in cursor.fetchall()
        ]
    finally:
        _fechar(connection, cursor)


def listar_estoque():
    """Todos os produtos, dos zerados para os mais cheios."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_produto, nome, categoria, status, quantidade_estoque,
                      preco_compra_centavos, preco_venda_centavos,
                      quantidade_estoque * preco_compra_centavos AS valor_estoque_centavos
               FROM produtos
               ORDER BY quantidade_estoque, nome, id_produto"""
        )
        return [
            {
                "id_produto": row["id_produto"],
                "nome": row["nome"],
                "categoria": row["categoria"],
                "status": row["status"],
                "quantidade_estoque": row["quantidade_estoque"],
                "preco_compra_centavos": row["preco_compra_centavos"],
                "preco_venda_centavos": row["preco_venda_centavos"],
                "valor_estoque_centavos": inteiro(row["valor_estoque_centavos"]),
            }
            for row in cursor.fetchall()
        ]
    finally:
        _fechar(connection, cursor)
