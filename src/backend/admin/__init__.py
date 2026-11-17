"""Módulo da administração (usuários, movimentações e relatórios) em camadas:
routes → controller → service → repository. Todas as rotas exigem ADMINISTRADOR."""
from .routes import admin_api

__all__ = ["admin_api"]
