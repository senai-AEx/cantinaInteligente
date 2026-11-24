"""Rotas do QR Code. Somente o administrador gera e imprime os códigos."""
from flask import Blueprint, Response, jsonify, request

from ..produtos import service as produto_service
from ..seguranca import somente_administrador
from . import service as qr_service

qr_api = Blueprint("qr_api", __name__, url_prefix="/api/qrcode")


def _base():
    return qr_service.url_base(request.host_url)


def _resposta_svg(conteudo):
    return Response(
        qr_service.desenhar_svg(conteudo),
        mimetype="image/svg+xml",
        headers={"Cache-Control": "no-store"},
    )


@somente_administrador
def informacoes():
    return jsonify(qr_service.informacoes(_base())), 200


@somente_administrador
def cantina_svg():
    return _resposta_svg(qr_service.url_cantina(_base()))


@somente_administrador
def produto_svg(id_produto):
    # Produto inexistente responde 404 (o serviço lança ProdutoNaoEncontrado).
    produto_service.consultar_produto(id_produto)
    return _resposta_svg(qr_service.url_produto(_base(), id_produto))


qr_api.add_url_rule("", view_func=informacoes, methods=["GET"])
qr_api.add_url_rule("/cantina.svg", view_func=cantina_svg, methods=["GET"])
qr_api.add_url_rule("/produtos/<int:id_produto>.svg", view_func=produto_svg, methods=["GET"])
