"""Camada de controle: lê a requisição HTTP, chama o serviço e monta a resposta."""
from functools import wraps

from flask import current_app, jsonify, request
import mysql.connector

from . import service as produto_service
from .service import ErroValidacao, ProdutoNaoEncontrado

STATUS_VALIDOS = {"TODOS", "ATIVO", "INATIVO"}


def _resposta_erros_campos(campos, status=422):
    return jsonify(erro="Revise os campos informados.", campos=campos), status


def _autor():
    autor = request.headers.get("X-Actor", "").strip()
    return autor or "administrador-local"


def _tratar_erros(mensagem_banco):
    """Converte exceções do serviço/banco em respostas JSON padronizadas."""

    def decorador(funcao):
        @wraps(funcao)
        def envolvida(*args, **kwargs):
            try:
                return funcao(*args, **kwargs)
            except ErroValidacao as exc:
                return _resposta_erros_campos(exc.campos)
            except ProdutoNaoEncontrado:
                return jsonify(erro="Produto não encontrado."), 404
            except RuntimeError as exc:
                return jsonify(erro=str(exc)), 503
            except mysql.connector.Error:
                current_app.logger.exception(mensagem_banco)
                return jsonify(erro=mensagem_banco), 503

        return envolvida

    return decorador


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


@_tratar_erros("Não foi possível consultar os produtos.")
def listar_produtos():
    termo = request.args.get("q", "").strip()
    status = request.args.get("status", "TODOS").strip().upper() or "TODOS"
    if len(termo) > 100:
        return _resposta_erros_campos({"q": "A busca pode ter no máximo 100 caracteres."})
    if status not in STATUS_VALIDOS:
        return _resposta_erros_campos({"status": "Use TODOS, ATIVO ou INATIVO na consulta."})
    return jsonify(produto_service.listar_produtos(termo, status)), 200


@_tratar_erros("Não foi possível consultar o produto.")
def consultar_produto(id_produto):
    return jsonify(produto=produto_service.consultar_produto(id_produto)), 200


@_tratar_erros("Não foi possível cadastrar o produto.")
def incluir_produto():
    payload, erro = _ler_payload()
    if erro:
        return erro
    produto = produto_service.incluir_produto(payload, _autor(), request.path)
    return jsonify(produto=produto), 201, {
        "Location": f"/api/produtos/{produto['id_produto']}"
    }


@_tratar_erros("Não foi possível alterar o produto.")
def alterar_produto(id_produto):
    payload, erro = _ler_payload()
    if erro:
        return erro
    produto = produto_service.alterar_produto(id_produto, payload, _autor(), request.path)
    return jsonify(produto=produto), 200


@_tratar_erros("Não foi possível excluir (inativar) o produto.")
def inativar_produto(id_produto):
    produto = produto_service.inativar_produto(id_produto, _autor(), request.path)
    return jsonify(produto=produto), 200


@_tratar_erros("Não foi possível reativar o produto.")
def reativar_produto(id_produto):
    produto = produto_service.reativar_produto(id_produto, _autor(), request.path)
    return jsonify(produto=produto), 200


@_tratar_erros("Não foi possível consultar a auditoria.")
def listar_auditoria(id_produto):
    return jsonify(auditorias=produto_service.listar_auditoria(id_produto)), 200
