.PHONY: help setup up demo admin credenciais migrate seed backup restore test

# Atalhos opcionais. Os comandos de verdade são: python instalar.py e python iniciar.py
PYTHON ?= python

help:
	@echo Comandos (todos rodam tambem direto com python):
	@echo   make setup        python instalar.py
	@echo   make up           python iniciar.py
	@echo   make demo         produtos de exemplo e usuarios de demonstracao
	@echo   make admin        recria o administrador com os dados do .env
	@echo   make credenciais  mostra os dados de acesso de demonstracao
	@echo   make migrate      aplica as migracoes que faltam
	@echo   make backup       grava uma copia do banco em backups/
	@echo   make restore ARQUIVO=backups/arquivo.sql
	@echo   make test         roda os testes automatizados

setup:
	$(PYTHON) instalar.py

up:
	$(PYTHON) iniciar.py

demo:
	$(PYTHON) scripts/banco.py semear
	$(PYTHON) scripts/criar_demo.py

admin:
	$(PYTHON) scripts/criar_admin.py

credenciais:
	$(PYTHON) scripts/credenciais.py

migrate:
	$(PYTHON) scripts/banco.py migrar

seed:
	$(PYTHON) scripts/banco.py semear

backup:
	$(PYTHON) scripts/banco.py backup

restore:
	$(PYTHON) scripts/banco.py restaurar $(ARQUIVO)

test:
	$(PYTHON) scripts/testes.py
