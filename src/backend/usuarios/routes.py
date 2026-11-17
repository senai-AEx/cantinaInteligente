"""Rotas de autenticação. Cada rota apenas delega para o controller."""
from flask import Blueprint

from . import controller as usuario_controller

auth_api = Blueprint("auth_api", __name__, url_prefix="/api/auth")

auth_api.add_url_rule("/cadastro", view_func=usuario_controller.cadastrar, methods=["POST"])
auth_api.add_url_rule("/login", view_func=usuario_controller.login, methods=["POST"])
auth_api.add_url_rule("/logout", view_func=usuario_controller.logout, methods=["POST"])
auth_api.add_url_rule("/eu", view_func=usuario_controller.eu, methods=["GET"])
