"""Camada de repositório: todo o SQL da tabela de produtos e da auditoria."""
from datetime import date, datetime, timezone
import json

from ..conexao import conectar, transacao  # noqa: F401  (transacao é usada pelo service)

COLUNAS_PRODUTO = """id_produto, nome, descricao, categoria,
    preco_compra_centavos, preco_venda_centavos, quantidade_estoque,
    foto_caminho, zero_lactose, zero_acucar, status, criado_em, atualizado_em"""

CAMPOS_GRAVAVEIS = (
    "nome",
    "descricao",
    "categoria",
    "preco_compra_centavos",
    "preco_venda_centavos",
    "quantidade_estoque",
    "foto_caminho",
    "zero_lactose",
    "zero_acucar",
)


def _fechar(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def _data_utc(valor):
    if isinstance(valor, datetime):
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=timezone.utc)
        return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(valor, date):
        return valor.isoformat()
    return valor


def produto_json(row):
    if row is None:
        return None
    produto = dict(row)
    for chave in ("criado_em", "atualizado_em"):
        produto[chave] = _data_utc(produto.get(chave))
    for chave in ("zero_lactose", "zero_acucar"):
        produto[chave] = bool(produto.get(chave))
    return produto


# ---------- consultas com conexão própria ----------

def listar_produtos(termo, status):
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        sql = f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE 1 = 1"
        params = []
        if termo:
            busca = f"%{termo}%"
            sql += " AND (nome LIKE %s OR categoria LIKE %s"
            params.extend((busca, busca))
            if termo.isdigit():
                sql += " OR id_produto = %s"
                params.append(int(termo))
            sql += ")"
        if status != "TODOS":
            sql += " AND status = %s"
            params.append(status)
        sql += " ORDER BY nome, id_produto"
        cursor.execute(sql, params)
        return [produto_json(row) for row in cursor.fetchall()]
    finally:
        _fechar(connection, cursor)


def consultar_produto(id_produto):
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        return carregar(cursor, id_produto)
    finally:
        _fechar(connection, cursor)


def listar_auditoria(id_produto):
    """Retorna (produto_existe, registros mais recentes primeiro)."""
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_produto FROM produtos WHERE id_produto = %s", (id_produto,)
        )
        produto_existe = cursor.fetchone() is not None
        cursor.execute(
            """SELECT id_auditoria, id_produto, acao, autor, origem,
                      antes_json, depois_json, registrado_em
               FROM auditoria_produtos
               WHERE id_produto = %s
               ORDER BY registrado_em DESC, id_auditoria DESC
               LIMIT 100""",
            (id_produto,),
        )
        registros = []
        for row in cursor.fetchall():
            item = dict(row)
            for chave in ("antes_json", "depois_json"):
                if isinstance(item[chave], (str, bytes, bytearray)):
                    item[chave] = json.loads(item[chave])
            item["registrado_em"] = _data_utc(item["registrado_em"])
            registros.append(item)
        return produto_existe, registros
    finally:
        _fechar(connection, cursor)


# ---------- operações dentro de uma transação (recebem o cursor) ----------

def carregar(cursor, id_produto, bloquear=False):
    sql = f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE id_produto = %s"
    if bloquear:
        sql += " FOR UPDATE"
    cursor.execute(sql, (id_produto,))
    return produto_json(cursor.fetchone())


def inserir(cursor, dados):
    colunas = ", ".join(CAMPOS_GRAVAVEIS)
    marcadores = ", ".join(["%s"] * len(CAMPOS_GRAVAVEIS))
    cursor.execute(
        f"INSERT INTO produtos ({colunas}) VALUES ({marcadores})",
        tuple(dados[campo] for campo in CAMPOS_GRAVAVEIS),
    )
    return cursor.lastrowid


def atualizar(cursor, id_produto, dados):
    atribuicoes = ", ".join(f"{campo} = %s" for campo in CAMPOS_GRAVAVEIS)
    cursor.execute(
        f"UPDATE produtos SET {atribuicoes} WHERE id_produto = %s",
        tuple(dados[campo] for campo in CAMPOS_GRAVAVEIS) + (id_produto,),
    )


def atualizar_status(cursor, id_produto, status):
    cursor.execute(
        "UPDATE produtos SET status = %s WHERE id_produto = %s",
        (status, id_produto),
    )


def registrar_auditoria(cursor, id_produto, acao, autor, origem, antes, depois):
    cursor.execute(
        """INSERT INTO auditoria_produtos
               (id_produto, acao, autor, origem, antes_json, depois_json)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            id_produto,
            acao,
            autor[:100],
            origem[:100],
            json.dumps(antes, ensure_ascii=False) if antes is not None else None,
            json.dumps(depois, ensure_ascii=False),
        ),
    )
