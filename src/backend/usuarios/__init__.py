"""Módulo de usuários: cadastro, autenticação e senha (routes → controller → service → repository)."""
from .routes import auth_api, usuarios_admin_api

__all__ = ["auth_api", "usuarios_admin_api"]
