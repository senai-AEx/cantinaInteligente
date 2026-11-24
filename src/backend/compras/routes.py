"""Rotas HTTP de compras: recebem a requisição, chamam o serviço e devolvem JSON.

Todas as rotas exigem login. A compra é sempre registrada para o usuário logado.
Não existe rota para alterar ou apagar uma compra: o histórico é permanente.
"""
from flask import Blueprint, jsonify

from ..http import ler_json, ler_limite
from ..seguranca import login_obrigatorio, usuario_atual
from . import service as compra_service

compras_api = Blueprint("compras_api", __name__, url_prefix="/api/compras")


@login_obrigatorio
def registrar_compra():
    """201 quando a compra foi gravada; 200 quando a chave já tinha sido usada."""
    compra, carteira, criada = compra_service.registrar_compra(usuario_atual(), ler_json())
    return jsonify(compra=compra, carteira=carteira), 201 if criada else 200


@login_obrigatorio
def listar_compras():
    limite = ler_limite(padrao=50, maximo=200)
    return jsonify(compras=compra_service.listar_compras(usuario_atual(), limite)), 200


@login_obrigatorio
def consultar_compra(id_compra):
    return jsonify(compra=compra_service.consultar_compra(usuario_atual(), id_compra)), 200


compras_api.add_url_rule("", view_func=registrar_compra, methods=["POST"])
compras_api.add_url_rule("", view_func=listar_compras, methods=["GET"])
compras_api.add_url_rule("/<int:id_compra>", view_func=consultar_compra, methods=["GET"])
