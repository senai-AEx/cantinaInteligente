"""Camada de controle: lê a requisição HTTP, chama o serviço e monta a resposta.

Todas as rotas exigem login e sempre atuam na carteira do usuário logado.
Os erros lançados pelo serviço viram respostas JSON no app.py.
"""
from flask import jsonify

from ..http import ler_json, ler_limite
from ..seguranca import login_obrigatorio, usuario_atual
from . import service as carteira_service


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
