from flask import jsonify, request
import mysql.connector

from . import service as produto_service

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
# Listar todos os produtos
def listar_produtos():
    termo = request.args.get("q", "").strip()
    status = request.args.get("status", "TODOS").strip().upper() or "TODOS"

    if len(termo) > 100:
        return _resposta_erros_campos({"q": "A busca pode ter no máximo 100 caracteres."})

    if status not in {"TODOS", "ATIVO", "INATIVO"}:
        return _resposta_erros_campos(
            {"status": "Use TODOS, ATIVO ou INATIVO na consulta."}
        )

    try:
        produtos = produto_service.listar_produtos(termo, status)
        return jsonify(produtos), 200

    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503

    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível consultar os produtos.")


# Consultar produto por ID
def consultar_produto(id_produto):
    try:
        produto = produto_service.consultar_produto(id_produto)

        if produto is None:
            return jsonify(erro="Produto não encontrado."), 404

        return jsonify(produto=produto), 200

    except RuntimeError as exc:
        return jsonify(erro=str(exc)), 503

    except mysql.connector.Error as exc:
        return _db_error(exc, "Não foi possível consultar o produto.")



# Funções auxiliares
def _db_error(exc, message="Falha ao acessar o banco de dados."):
    if getattr(exc, "errno", None) == 1062:
        return _resposta_erros_campos(
            {"codigo_produto": "Já existe um produto com este código."}
        )
    return jsonify(erro=message), 503

def _resposta_erros_campos(errors, status=422):
    return jsonify(erro="Revise os campos informados.", campos=errors), status
