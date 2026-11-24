"""Rotas HTTP da carteira: saldo, extrato e declaração de crédito.

Todas as rotas exigem login e sempre atuam na carteira do usuário logado.
"""
from flask import Blueprint, jsonify

from ..http import ler_json, ler_limite
from ..seguranca import login_obrigatorio, usuario_atual
from . import service as carteira_service

carteira_api = Blueprint("carteira_api", __name__, url_prefix="/api/carteira")


@login_obrigatorio
def consultar_carteira():
    return jsonify(carteira=carteira_service.consultar_carteira(usuario_atual())), 200


@login_obrigatorio
def listar_movimentacoes():
    limite = ler_limite(padrao=50, maximo=200)
    movimentacoes = carteira_service.listar_movimentacoes(usuario_atual(), limite)
    return jsonify(movimentacoes=movimentacoes), 200


@login_obrigatorio
def adicionar_credito():
    """201 quando o crédito foi lançado; 200 quando a chave já tinha sido usada."""
    movimentacao, carteira, criado = carteira_service.adicionar_credito(
        usuario_atual(), ler_json()
    )
    return jsonify(movimentacao=movimentacao, carteira=carteira), 201 if criado else 200


carteira_api.add_url_rule("", view_func=consultar_carteira, methods=["GET"])
carteira_api.add_url_rule("/movimentacoes", view_func=listar_movimentacoes, methods=["GET"])
carteira_api.add_url_rule("/creditos", view_func=adicionar_credito, methods=["POST"])
