"""Rotas HTTP da carteira. Cada rota apenas delega para o controller."""
from flask import Blueprint

from . import controller as carteira_controller

carteira_api = Blueprint("carteira_api", __name__, url_prefix="/api/carteira")

carteira_api.add_url_rule(
    "", view_func=carteira_controller.consultar_carteira, methods=["GET"]
)
carteira_api.add_url_rule(
    "/movimentacoes", view_func=carteira_controller.listar_movimentacoes, methods=["GET"]
)
carteira_api.add_url_rule(
    "/creditos", view_func=carteira_controller.adicionar_credito, methods=["POST"]
)
