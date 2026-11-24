"""Rotas HTTP da administração: usuários, ajustes de saldo, movimentações, relatórios e compras.

Todas as rotas exigem o perfil ADMINISTRADOR. Os erros lançados pelo serviço
(`erros.py`) viram JSON no `app.py`; por isso não há try/except aqui.

Não existe rota DELETE: usuários não são apagados, apenas inativados
(`PATCH /api/admin/usuarios/<id>/inativar`).
"""
from flask import Blueprint, jsonify, request

from ..http import ler_json, ler_limite
from ..seguranca import somente_administrador, usuario_atual
from . import service as admin_service

admin_api = Blueprint("admin_api", __name__, url_prefix="/api/admin")


# ---------- usuários ----------

@somente_administrador
def listar_usuarios():
    usuarios = admin_service.listar_usuarios(
        request.args.get("q", ""),
        request.args.get("status", ""),
        request.args.get("perfil", ""),
    )
    return jsonify(usuarios=usuarios), 200


@somente_administrador
def consultar_usuario(id_usuario):
    return jsonify(usuario=admin_service.consultar_usuario(id_usuario)), 200


@somente_administrador
def alterar_usuario(id_usuario):
    usuario = admin_service.alterar_usuario(id_usuario, ler_json(), usuario_atual())
    return jsonify(usuario=usuario), 200


@somente_administrador
def inativar_usuario(id_usuario):
    usuario = admin_service.inativar_usuario(id_usuario, usuario_atual())
    return jsonify(usuario=usuario), 200


@somente_administrador
def reativar_usuario(id_usuario):
    return jsonify(usuario=admin_service.reativar_usuario(id_usuario)), 200


@somente_administrador
def ajustar_saldo(id_usuario):
    movimentacao, carteira, criado = admin_service.ajustar_saldo(
        id_usuario, ler_json(), usuario_atual()
    )
    # Chave de idempotência repetida: devolve o ajuste já gravado com 200.
    return jsonify(movimentacao=movimentacao, carteira=carteira), 201 if criado else 200


# ---------- movimentações ----------

@somente_administrador
def listar_movimentacoes():
    resposta = admin_service.listar_movimentacoes(
        request.args.get("de", ""),
        request.args.get("ate", ""),
        request.args.get("tipo", ""),
        request.args.get("id_usuario", ""),
        ler_limite(padrao=200, maximo=500),
    )
    return jsonify(resposta), 200


# ---------- relatórios ----------

@somente_administrador
def relatorio_vendas():
    relatorio = admin_service.relatorio_vendas(
        request.args.get("de", ""), request.args.get("ate", "")
    )
    return jsonify(relatorio), 200


@somente_administrador
def relatorio_saldos():
    return jsonify(admin_service.relatorio_saldos()), 200


@somente_administrador
def relatorio_estoque():
    return jsonify(admin_service.relatorio_estoque()), 200


@somente_administrador
def listar_compras():
    """Compras registradas: quem comprou o quê no período."""
    resposta = admin_service.listar_compras(
        request.args.get("de", ""),
        request.args.get("ate", ""),
        request.args.get("id_usuario", ""),
        ler_limite(padrao=100, maximo=500),
    )
    return jsonify(resposta), 200


admin_api.add_url_rule("/usuarios", view_func=listar_usuarios, methods=["GET"])
admin_api.add_url_rule("/usuarios/<int:id_usuario>", view_func=consultar_usuario, methods=["GET"])
admin_api.add_url_rule("/usuarios/<int:id_usuario>", view_func=alterar_usuario, methods=["PUT"])
admin_api.add_url_rule("/usuarios/<int:id_usuario>/inativar", view_func=inativar_usuario, methods=["PATCH"])
admin_api.add_url_rule("/usuarios/<int:id_usuario>/reativar", view_func=reativar_usuario, methods=["PATCH"])
admin_api.add_url_rule("/usuarios/<int:id_usuario>/ajustes", view_func=ajustar_saldo, methods=["POST"])
admin_api.add_url_rule("/movimentacoes", view_func=listar_movimentacoes, methods=["GET"])
admin_api.add_url_rule("/relatorios/vendas", view_func=relatorio_vendas, methods=["GET"])
admin_api.add_url_rule("/relatorios/saldos", view_func=relatorio_saldos, methods=["GET"])
admin_api.add_url_rule("/relatorios/estoque", view_func=relatorio_estoque, methods=["GET"])
admin_api.add_url_rule("/compras", view_func=listar_compras, methods=["GET"])
