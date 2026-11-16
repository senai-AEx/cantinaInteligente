from backend.conexao import conectar
from datetime import date, datetime, timezone

COLUNAS_PRODUTO = """id_produto, codigo_produto, nome, descricao, categoria,
    preco_centavos, quantidade_estoque, estoque_minimo, estoque_maximo,
    validade, foto_caminho, zero_lactose, zero_acucar, status,
    criado_em, atualizado_em"""


# Listar todos os produtos
def listar_produtos(termo, status):
    connection = None
    cursor = None

    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)

        sql = f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE 1 = 1"
        params = []

        if termo:
            sql += " AND (codigo_produto LIKE %s OR nome LIKE %s OR categoria LIKE %s)"
            busca = f"%{termo}%"
            params.extend((busca, busca, busca))

        if status != "TODOS":
            sql += " AND status = %s"
            params.append(status)

        sql += " ORDER BY nome, id_produto"

        cursor.execute(sql, params)
        return [_produto_json(row) for row in cursor.fetchall()]

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

# Consultar produto por ID
def consultar_produto(id_produto):
    connection = None
    cursor = None

    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)

        produto = _carregar(cursor, id_produto)

        return produto

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# Funções auxiliares
def _produto_json(row):
    if row is None:
        return None
    result = dict(row)
    for key in ("validade",):
        if isinstance(result.get(key), (date, datetime)):
            result[key] = result[key].isoformat()
    for key in ("criado_em", "atualizado_em"):
        value = result.get(key)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            result[key] = value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    for key in ("zero_lactose", "zero_acucar"):
        result[key] = bool(result[key])
    return result


def _carregar(cursor, id_produto, bloquear=False):
    sql = f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE id_produto = %s"
    if bloquear:
        sql += " FOR UPDATE"
    cursor.execute(sql, (id_produto,))
    return _produto_json(cursor.fetchone())