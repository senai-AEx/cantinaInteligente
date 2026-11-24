"""Sessão de login e controle de acesso por perfil.

A sessão fica em um cookie assinado pelo Flask (HttpOnly) e guarda apenas o
id do usuário. A cada requisição o usuário é relido do banco, de modo que um
usuário inativado ou que perdeu o perfil de administrador perde o acesso na hora.

Uso nas rotas:

    @login_obrigatorio
    def minha_rota():
        usuario = usuario_atual()

    @somente_administrador
    def rota_admin(): ...
"""
from functools import wraps

from flask import g, session

from .erros import NaoAutenticado, SemPermissao

PERFIL_ADMINISTRADOR = "ADMINISTRADOR"
PERFIL_CLIENTE = "CLIENTE"


def carregar_usuario(id_usuario):
    """Busca o usuário no banco. Função separada para os testes substituírem."""
    from .usuarios import repository as usuario_repository

    return usuario_repository.buscar_por_id(id_usuario)


def iniciar_sessao(usuario):
    session.clear()
    session["id_usuario"] = usuario["id_usuario"]
    session.permanent = True
    g.usuario = usuario


def encerrar_sessao():
    session.clear()
    g.usuario = None


def usuario_atual():
    """Usuário logado e ativo, ou None."""
    if "usuario" not in g:
        id_usuario = session.get("id_usuario")
        usuario = carregar_usuario(id_usuario) if id_usuario else None
        if usuario is not None and usuario.get("status") != "ATIVO":
            usuario = None
        if usuario is None and id_usuario:
            session.clear()
        g.usuario = usuario
    return g.usuario


def eh_administrador(usuario):
    return bool(usuario) and usuario.get("perfil") == PERFIL_ADMINISTRADOR


def login_obrigatorio(funcao):
    @wraps(funcao)
    def envolvida(*args, **kwargs):
        if usuario_atual() is None:
            raise NaoAutenticado()
        return funcao(*args, **kwargs)

    return envolvida


def somente_administrador(funcao):
    @wraps(funcao)
    def envolvida(*args, **kwargs):
        usuario = usuario_atual()
        if usuario is None:
            raise NaoAutenticado()
        if not eh_administrador(usuario):
            raise SemPermissao("Esta área é exclusiva da administração da cantina.")
        return funcao(*args, **kwargs)

    return envolvida


def autor_auditoria():
    """Texto que identifica o usuário logado nos registros de auditoria."""
    usuario = usuario_atual()
    if usuario is None:
        return "anonimo"
    return f"{usuario['nome']} (#{usuario['id_usuario']})"[:100]
