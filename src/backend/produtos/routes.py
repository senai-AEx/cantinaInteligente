"""Rotas HTTP de produtos: recebem a requisição, chamam o serviço e devolvem JSON.

Consultar produtos é público (o catálogo aparece sem login). Cadastrar, alterar,
inativar, reativar e ver a auditoria exigem perfil de administrador.

Não existe rota DELETE: excluir um produto é feito pela inativação
(`PATCH /api/produtos/<id>/inativar`), que mantém o registro no banco.
"""
from flask import Blueprint, jsonify, request

from ..erros import ErroValidacao
from ..http import ler_json
from ..seguranca import autor_auditoria, eh_administrador, somente_administrador, usuario_atual
from . import service as produto_service

produtos_api = Blueprint("produtos_api", __name__, url_prefix="/api/produtos")

STATUS_VALIDOS = {"TODOS", "ATIVO", "INATIVO"}


def _visao_publica(produto):
    """O catálogo não mostra o preço de compra (custo); só a administração vê."""
    return {chave: valor for chave, valor in produto.items() if chave != "preco_compra_centavos"}


def listar_produtos():
    termo = request.args.get("q", "").strip()
    status = request.args.get("status", "TODOS").strip().upper() or "TODOS"
    if len(termo) > 100:
        raise ErroValidacao({"q": "A busca pode ter no máximo 100 caracteres."})
    if status not in STATUS_VALIDOS:
        raise ErroValidacao({"status": "Use TODOS, ATIVO ou INATIVO na consulta."})
    if eh_administrador(usuario_atual()):
        return jsonify(produto_service.listar_produtos(termo, status)), 200
    # Visitantes e clientes veem somente produtos ativos, sem o preço de compra.
    produtos = produto_service.listar_produtos(termo, "ATIVO")
    return jsonify([_visao_publica(produto) for produto in produtos]), 200


def consultar_produto(id_produto):
    produto = produto_service.consultar_produto(id_produto)
    if eh_administrador(usuario_atual()):
        return jsonify(produto=produto), 200
    if produto["status"] != "ATIVO":
        raise produto_service.ProdutoNaoEncontrado()
    return jsonify(produto=_visao_publica(produto)), 200


@somente_administrador
def incluir_produto():
    produto = produto_service.incluir_produto(ler_json(), autor_auditoria(), request.path)
    return jsonify(produto=produto), 201, {
        "Location": f"/api/produtos/{produto['id_produto']}"
    }


@somente_administrador
def alterar_produto(id_produto):
    produto = produto_service.alterar_produto(
        id_produto, ler_json(), autor_auditoria(), request.path
    )
    return jsonify(produto=produto), 200


@somente_administrador
def inativar_produto(id_produto):
    """Exclusão lógica: o produto fica INATIVO e continua no banco."""
    produto = produto_service.inativar_produto(id_produto, autor_auditoria(), request.path)
    return jsonify(produto=produto), 200


@somente_administrador
def reativar_produto(id_produto):
    produto = produto_service.reativar_produto(id_produto, autor_auditoria(), request.path)
    return jsonify(produto=produto), 200


@somente_administrador
def listar_auditoria(id_produto):
    return jsonify(auditorias=produto_service.listar_auditoria(id_produto)), 200


produtos_api.add_url_rule("", view_func=listar_produtos, methods=["GET"])
produtos_api.add_url_rule("", view_func=incluir_produto, methods=["POST"])
produtos_api.add_url_rule("/<int:id_produto>", view_func=consultar_produto, methods=["GET"])
produtos_api.add_url_rule("/<int:id_produto>", view_func=alterar_produto, methods=["PUT"])
produtos_api.add_url_rule("/<int:id_produto>/inativar", view_func=inativar_produto, methods=["PATCH"])
produtos_api.add_url_rule("/<int:id_produto>/reativar", view_func=reativar_produto, methods=["PATCH"])
produtos_api.add_url_rule("/<int:id_produto>/auditoria", view_func=listar_auditoria, methods=["GET"])
