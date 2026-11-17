"""Camada de controle: lê a requisição HTTP, chama o serviço e monta a resposta.

Consultar produtos é público (o catálogo aparece sem login). Cadastrar, alterar,
inativar, reativar e ver a auditoria exigem perfil de administrador.
Os erros lançados pelo serviço viram respostas JSON no app.py.
"""
from flask import jsonify, request

from ..erros import ErroValidacao
from ..http import ler_json
from ..seguranca import autor_auditoria, eh_administrador, somente_administrador, usuario_atual
from . import service as produto_service

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
