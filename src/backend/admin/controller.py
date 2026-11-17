"""Camada de controle da administração: lê a requisição, chama o serviço e monta a resposta.

Todas as rotas exigem o perfil ADMINISTRADOR. Os erros lançados pelo serviço
(`erros.py`) viram JSON no `app.py`; por isso não há try/except aqui.
"""
from flask import jsonify, request

from ..http import ler_json, ler_limite
from ..seguranca import somente_administrador, usuario_atual
from . import service as admin_service


# ---------- usuários ----------

@somente_administrador
def listar_usuarios():
    usuarios = admin_service.listar_usuarios(
        request.args.get("q", ""),
        request.args.get("status", ""),
        request.args.get("perfil", ""),
    )
    return jsonify(usuarios=usuarios), 200


@somente_administrador
def consultar_usuario(id_usuario):
    return jsonify(usuario=admin_service.consultar_usuario(id_usuario)), 200


@somente_administrador
def alterar_usuario(id_usuario):
    usuario = admin_service.alterar_usuario(id_usuario, ler_json(), usuario_atual())
    return jsonify(usuario=usuario), 200


@somente_administrador
def inativar_usuario(id_usuario):
    usuario = admin_service.inativar_usuario(id_usuario, usuario_atual())
    return jsonify(usuario=usuario), 200


@somente_administrador
def reativar_usuario(id_usuario):
    return jsonify(usuario=admin_service.reativar_usuario(id_usuario)), 200


@somente_administrador
def ajustar_saldo(id_usuario):
    movimentacao, carteira, criado = admin_service.ajustar_saldo(
        id_usuario, ler_json(), usuario_atual()
    )
    # Chave de idempotência repetida: devolve o ajuste já gravado com 200.
    return jsonify(movimentacao=movimentacao, carteira=carteira), 201 if criado else 200


# ---------- movimentações ----------

@somente_administrador
def listar_movimentacoes():
    resposta = admin_service.listar_movimentacoes(
        request.args.get("de", ""),
        request.args.get("ate", ""),
        request.args.get("tipo", ""),
        request.args.get("id_usuario", ""),
        ler_limite(padrao=200, maximo=500),
    )
    return jsonify(resposta), 200


# ---------- relatórios ----------

@somente_administrador
def relatorio_vendas():
    relatorio = admin_service.relatorio_vendas(
        request.args.get("de", ""), request.args.get("ate", "")
    )
    return jsonify(relatorio), 200


@somente_administrador
def relatorio_saldos():
    return jsonify(admin_service.relatorio_saldos()), 200


@somente_administrador
def relatorio_estoque():
    return jsonify(admin_service.relatorio_estoque()), 200
