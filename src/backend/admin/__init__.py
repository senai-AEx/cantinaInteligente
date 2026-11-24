"""Módulo da administração (usuários, movimentações e relatórios).
Rotas em routes.py, regras em service.py, SQL em repository.py. Todas as rotas exigem ADMINISTRADOR."""
from .routes import admin_api

__all__ = ["admin_api"]
