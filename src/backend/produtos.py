"""Rotas da API de manutenção de produtos da AV04."""
from datetime import date, datetime, timezone
import json

import mysql.connector
from flask import Blueprint, jsonify, request

from .conexao import conectar, transacao
from .validacao_produtos import validar_produto

produtos_api = Blueprint("produtos_api", __name__)

COLUNAS_PRODUTO = """id_produto, codigo_produto, nome, descricao, categoria,
    preco_centavos, quantidade_estoque, estoque_minimo, estoque_maximo,
    validade, foto_caminho, zero_lactose, zero_acucar, status,
    criado_em, atualizado_em"""
CAMPOS_GRAVAVEIS = (
    "codigo_produto",
    "nome",
    "descricao",
    "categoria",
    "preco_centavos",
    "quantidade_estoque",
    "estoque_minimo",
    "estoque_maximo",
    "validade",
    "foto_caminho",
    "zero_lactose",
    "zero_acucar",
)


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


def _resposta_erros_campos(errors, status=422):
    return jsonify(erro="Revise os campos informados.", campos=errors), status


def _ler_payload():
    if not request.is_json:
        return None, (jsonify(erro="Envie o corpo como application/json."), 400)
    payload = request.get_json(silent=True)
    if payload is None:
        return None, (jsonify(erro="O JSON enviado está vazio ou malformado."), 400)
    if not isinstance(payload, dict):
        return None, _resposta_erros_campos(
            {"_geral": "Envie um objeto JSON com os dados do produto."}
        )
    return payload, None


def _auditoria(cursor, id_produto, acao, antes, depois):
    autor = request.headers.get("X-Actor", "administrador-local").strip()
    origem = request.path
    cursor.execute(
        """INSERT INTO auditoria_produtos
               (id_produto, acao, autor, origem, antes_json, depois_json)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            id_produto,
            acao,
            (autor or "administrador-local")[:100],
            origem[:100],
            json.dumps(antes, ensure_ascii=False) if antes is not None else None,
            json.dumps(depois, ensure_ascii=False),
        ),
    )


def _db_error(exc, message="Falha ao acessar o banco de dados."):
    if getattr(exc, "errno", None) == 1062:
        return _resposta_erros_campos(
            {"codigo_produto": "Já existe um produto com este código."}
        )
    return jsonify(erro=message), 503


@produtos_api.get("/api/produtos")
def listar_produtos():
    termo = request.args.get("q", "").strip()
    status = request.args.get("status", "TODOS").strip().upper() or "TODOS"
    if len(termo) > 100:
        return _resposta_erros_campos({"q": "A busca pode ter no máximo 100 caracteres."})
    if status not in {"TODOS", "ATIVO", "INATIVO"}:
        return _resposta_erros_campos(
            {"status": "Use TODOS, ATIVO ou INATIVO na consulta."}
        )

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
        return jsonify([_produto_json(row) for row in cursor.fetchall()]), 200
    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503
    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível consultar os produtos.")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@produtos_api.get("/api/produtos/<int:id_produto>")
def consultar_produto(id_produto):
    connection = None
    cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        produto = _carregar(cursor, id_produto)
        if produto is None:
            return jsonify(erro="Produto não encontrado."), 404
        return jsonify(produto=produto), 200
    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503
    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível consultar o produto.")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@produtos_api.post("/api/produtos")
def incluir_produto():
    payload, error_response = _ler_payload()
    if error_response:
        return error_response
    dados, errors = validar_produto(payload)
    if errors:
        return _resposta_erros_campos(errors)

    try:
        with transacao() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                placeholders = ", ".join(["%s"] * len(CAMPOS_GRAVAVEIS))
                columns = ", ".join(CAMPOS_GRAVAVEIS)
                values = tuple(dados[field] for field in CAMPOS_GRAVAVEIS)
                cursor.execute(
                    f"INSERT INTO produtos ({columns}) VALUES ({placeholders})", values
                )
                id_produto = cursor.lastrowid
                produto = _carregar(cursor, id_produto)
                _auditoria(cursor, id_produto, "INCLUIR", None, produto)
            finally:
                cursor.close()
        return jsonify(produto=produto), 201, {
            "Location": f"/api/produtos/{id_produto}"
        }
    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503
    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível cadastrar o produto.")


@produtos_api.put("/api/produtos/<int:id_produto>")
def alterar_produto(id_produto):
    payload, error_response = _ler_payload()
    if error_response:
        return error_response
    dados, errors = validar_produto(payload)
    if errors:
        return _resposta_erros_campos(errors)

    try:
        with transacao() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                antes = _carregar(cursor, id_produto, bloquear=True)
                if antes is None:
                    return jsonify(erro="Produto não encontrado."), 404
                assignments = ", ".join(f"{field} = %s" for field in CAMPOS_GRAVAVEIS)
                values = tuple(dados[field] for field in CAMPOS_GRAVAVEIS) + (id_produto,)
                cursor.execute(
                    f"UPDATE produtos SET {assignments} WHERE id_produto = %s", values
                )
                depois = _carregar(cursor, id_produto)
                _auditoria(cursor, id_produto, "ALTERAR", antes, depois)
            finally:
                cursor.close()
        return jsonify(produto=depois), 200
    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503
    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível alterar o produto.")


def _mudar_status(id_produto, status_novo, acao):
    try:
        with transacao() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                antes = _carregar(cursor, id_produto, bloquear=True)
                if antes is None:
                    return jsonify(erro="Produto não encontrado."), 404
                if antes["status"] == status_novo:
                    return jsonify(produto=antes), 200
                cursor.execute(
                    "UPDATE produtos SET status = %s WHERE id_produto = %s",
                    (status_novo, id_produto),
                )
                depois = _carregar(cursor, id_produto)
                _auditoria(cursor, id_produto, acao, antes, depois)
            finally:
                cursor.close()
        return jsonify(produto=depois), 200
    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503
    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível alterar a situação do produto.")


@produtos_api.delete("/api/produtos/<int:id_produto>")
def inativar_produto(id_produto):
    return _mudar_status(id_produto, "INATIVO", "INATIVAR")


@produtos_api.patch("/api/produtos/<int:id_produto>/reativar")
def reativar_produto(id_produto):
    return _mudar_status(id_produto, "ATIVO", "REATIVAR")


@produtos_api.get("/api/produtos/<int:id_produto>/auditoria")
def listar_auditoria(id_produto):
    connection = None
    cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_produto FROM produtos WHERE id_produto = %s", (id_produto,))
        if cursor.fetchone() is None:
            return jsonify(erro="Produto não encontrado."), 404
        cursor.execute(
            """SELECT id_auditoria, id_produto, acao, autor, origem,
                      antes_json, depois_json, registrado_em
               FROM auditoria_produtos
               WHERE id_produto = %s
               ORDER BY registrado_em DESC, id_auditoria DESC
               LIMIT 100""",
            (id_produto,),
        )
        records = []
        for row in cursor.fetchall():
            item = dict(row)
            for key in ("antes_json", "depois_json"):
                if isinstance(item[key], str):
                    item[key] = json.loads(item[key])
            when = item["registrado_em"]
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            item["registrado_em"] = when.astimezone(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            records.append(item)
        return jsonify(auditorias=records), 200
    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503
    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível consultar a auditoria.")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
