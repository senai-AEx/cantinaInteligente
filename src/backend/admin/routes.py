"""Rotas HTTP da administração. Cada rota apenas delega para o controller.

Não existe rota DELETE: usuários não são apagados, apenas inativados
(`PATCH /api/admin/usuarios/<id>/inativar`).
"""
from flask import Blueprint

from . import controller as admin_controller

admin_api = Blueprint("admin_api", __name__, url_prefix="/api/admin")

# ---------- usuários ----------

admin_api.add_url_rule(
    "/usuarios", view_func=admin_controller.listar_usuarios, methods=["GET"]
)
admin_api.add_url_rule(
    "/usuarios/<int:id_usuario>", view_func=admin_controller.consultar_usuario, methods=["GET"]
)
admin_api.add_url_rule(
    "/usuarios/<int:id_usuario>", view_func=admin_controller.alterar_usuario, methods=["PUT"]
)
admin_api.add_url_rule(
    "/usuarios/<int:id_usuario>/inativar",
    view_func=admin_controller.inativar_usuario,
    methods=["PATCH"],
)
admin_api.add_url_rule(
    "/usuarios/<int:id_usuario>/reativar",
    view_func=admin_controller.reativar_usuario,
    methods=["PATCH"],
)
admin_api.add_url_rule(
    "/usuarios/<int:id_usuario>/ajustes",
    view_func=admin_controller.ajustar_saldo,
    methods=["POST"],
)

# ---------- movimentações ----------

admin_api.add_url_rule(
    "/movimentacoes", view_func=admin_controller.listar_movimentacoes, methods=["GET"]
)

# ---------- relatórios ----------

admin_api.add_url_rule(
    "/relatorios/vendas", view_func=admin_controller.relatorio_vendas, methods=["GET"]
)
admin_api.add_url_rule(
    "/relatorios/saldos", view_func=admin_controller.relatorio_saldos, methods=["GET"]
)
admin_api.add_url_rule(
    "/relatorios/estoque", view_func=admin_controller.relatorio_estoque, methods=["GET"]
)
# Compras registradas (quem comprou o quê).
admin_api.add_url_rule(
    "/compras", view_func=admin_controller.listar_compras, methods=["GET"]
)
