"""Rotas HTTP de compras. Cada rota apenas delega para o controller.

Não existe rota para alterar ou apagar uma compra: o histórico é permanente.
"""
from flask import Blueprint

from . import controller as compra_controller

compras_api = Blueprint("compras_api", __name__, url_prefix="/api/compras")

compras_api.add_url_rule("", view_func=compra_controller.registrar_compra, methods=["POST"])
compras_api.add_url_rule("", view_func=compra_controller.listar_compras, methods=["GET"])
compras_api.add_url_rule(
    "/<int:id_compra>", view_func=compra_controller.consultar_compra, methods=["GET"]
)
