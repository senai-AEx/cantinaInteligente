"""Apoio aos testes: simula um usuário logado sem precisar de banco."""
from unittest.mock import patch

ADMINISTRADOR = {
    "id_usuario": 1,
    "nome": "Administradora Teste",
    "matricula": "100001",
    "cpf": "52998224725",
    "email": "admin@teste.local",
    "perfil": "ADMINISTRADOR",
    "status": "ATIVO",
    "saldo_centavos": 0,
    "criado_em": None,
}

CLIENTE = {
    "id_usuario": 2,
    "nome": "Cliente Teste",
    "matricula": "202600001",
    "cpf": "11144477735",
    "email": "cliente@teste.local",
    "perfil": "CLIENTE",
    "status": "ATIVO",
    "saldo_centavos": 1000,
    "criado_em": None,
}


def simular_login(teste, cliente_http, usuario):
    """Faz `cliente_http` agir como `usuario` até o fim do teste.

    Substitui a leitura do usuário no banco (seguranca.carregar_usuario) e grava
    o id na sessão, exatamente como o login real faz.
    """
    usuarios = {usuario["id_usuario"]: usuario}
    substituto = patch(
        "src.backend.seguranca.carregar_usuario", lambda id_usuario: usuarios.get(id_usuario)
    )
    substituto.start()
    teste.addCleanup(substituto.stop)
    with cliente_http.session_transaction() as sessao:
        sessao["id_usuario"] = usuario["id_usuario"]
