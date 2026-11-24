"""Módulo de usuários: cadastro, autenticação e senha. Rotas em routes.py, regras em service.py, SQL em repository.py."""
from .routes import auth_api, usuarios_admin_api

__all__ = ["auth_api", "usuarios_admin_api"]
