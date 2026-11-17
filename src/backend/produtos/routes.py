"""Rotas HTTP de produtos. Cada rota apenas delega para o controller.

Não existe rota DELETE: excluir um produto é feito pela inativação
(`PATCH /api/produtos/<id>/inativar`), que mantém o registro no banco.
"""
from flask import Blueprint

from . import controller as produto_controller

produtos_api = Blueprint("produtos_api", __name__, url_prefix="/api/produtos")

produtos_api.add_url_rule("", view_func=produto_controller.listar_produtos, methods=["GET"])
produtos_api.add_url_rule("", view_func=produto_controller.incluir_produto, methods=["POST"])
produtos_api.add_url_rule(
    "/<int:id_produto>", view_func=produto_controller.consultar_produto, methods=["GET"]
)
produtos_api.add_url_rule(
    "/<int:id_produto>", view_func=produto_controller.alterar_produto, methods=["PUT"]
)
produtos_api.add_url_rule(
    "/<int:id_produto>/inativar", view_func=produto_controller.inativar_produto, methods=["PATCH"]
)
produtos_api.add_url_rule(
    "/<int:id_produto>/reativar", view_func=produto_controller.reativar_produto, methods=["PATCH"]
)
produtos_api.add_url_rule(
    "/<int:id_produto>/auditoria", view_func=produto_controller.listar_auditoria, methods=["GET"]
)
