"""Rotas do QR Code. Cada rota apenas delega para o controller."""
from flask import Blueprint

from . import controller as qr_controller

qr_api = Blueprint("qr_api", __name__, url_prefix="/api/qrcode")

qr_api.add_url_rule("", view_func=qr_controller.informacoes, methods=["GET"])
qr_api.add_url_rule("/cantina.svg", view_func=qr_controller.cantina_svg, methods=["GET"])
qr_api.add_url_rule(
    "/produtos/<int:id_produto>.svg", view_func=qr_controller.produto_svg, methods=["GET"]
)
