"""Rotas de usuários: cadastro, login, logout, sessão e troca ou redefinição de senha."""
from flask import Blueprint, jsonify

from ..http import ler_json
from ..seguranca import (
    encerrar_sessao,
    iniciar_sessao,
    login_obrigatorio,
    somente_administrador,
    usuario_atual,
)
from . import service as usuario_service
from .repository import usuario_json

auth_api = Blueprint("auth_api", __name__, url_prefix="/api/auth")

# Redefinição de senha pelo administrador (fica aqui porque a regra é de usuários).
usuarios_admin_api = Blueprint("usuarios_admin_api", __name__, url_prefix="/api/admin/usuarios")


def cadastrar():
    usuario = usuario_service.cadastrar(ler_json())
    iniciar_sessao(usuario)
    return jsonify(usuario=usuario_json(usuario)), 201


def login():
    usuario = usuario_service.autenticar(ler_json())
    iniciar_sessao(usuario)
    return jsonify(usuario=usuario_json(usuario)), 200


def logout():
    encerrar_sessao()
    return jsonify(mensagem="Sessão encerrada."), 200


def eu():
    """Sempre responde 200: {"usuario": {...}} ou {"usuario": null}."""
    return jsonify(usuario=usuario_json(usuario_atual())), 200


@login_obrigatorio
def alterar_senha():
    usuario_service.alterar_senha(usuario_atual(), ler_json())
    return jsonify(mensagem="Senha alterada."), 200


@somente_administrador
def redefinir_senha(id_usuario):
    """O administrador define uma senha provisória e a informa ao usuário pessoalmente."""
    usuario = usuario_service.redefinir_senha(id_usuario, ler_json())
    return jsonify(usuario=usuario_json(usuario)), 200


auth_api.add_url_rule("/cadastro", view_func=cadastrar, methods=["POST"])
auth_api.add_url_rule("/login", view_func=login, methods=["POST"])
auth_api.add_url_rule("/logout", view_func=logout, methods=["POST"])
auth_api.add_url_rule("/eu", view_func=eu, methods=["GET"])
auth_api.add_url_rule("/senha", view_func=alterar_senha, methods=["PUT"])
usuarios_admin_api.add_url_rule("/<int:id_usuario>/senha", view_func=redefinir_senha, methods=["POST"])
