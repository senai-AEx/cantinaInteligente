"""Camada de controle: cadastro, login, logout e consulta da sessão."""
from flask import jsonify

from ..http import ler_json
from ..seguranca import encerrar_sessao, iniciar_sessao, usuario_atual
from . import service as usuario_service
from .repository import usuario_json


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
