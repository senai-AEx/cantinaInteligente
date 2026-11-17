"""Camada de controle: lê a requisição HTTP, chama o serviço e monta a resposta.

Todas as rotas exigem login. A compra é sempre registrada para o usuário logado.
Os erros lançados pelo serviço viram respostas JSON no app.py.
"""
from flask import jsonify

from ..http import ler_json, ler_limite
from ..seguranca import login_obrigatorio, usuario_atual
from . import service as compra_service


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
