PYTHON ?= python

.DEFAULT_GOAL := help
.PHONY: help setup up down db-up db-down migrate seed admin demo credenciais backup restore api test status

help:
	@$(PYTHON) scripts/dev.py help

setup:
	@$(PYTHON) scripts/dev.py setup

up:
	@$(PYTHON) scripts/dev.py up

down:
	@$(PYTHON) scripts/dev.py db-down

db-up:
	@$(PYTHON) scripts/dev.py db-up

db-down:
	@$(PYTHON) scripts/dev.py db-down

migrate:
	@$(PYTHON) scripts/dev.py migrate

seed:
	@$(PYTHON) scripts/dev.py seed

api:
	@$(PYTHON) scripts/dev.py api

admin:
	@$(PYTHON) scripts/dev.py admin

demo:
	@$(PYTHON) scripts/dev.py demo

credenciais:
	@$(PYTHON) scripts/dev.py credenciais

backup:
	@$(PYTHON) scripts/dev.py backup

restore:
	@$(PYTHON) scripts/dev.py restore $(ARQUIVO)

test:
	@$(PYTHON) scripts/dev.py test

status:
	@$(PYTHON) scripts/dev.py status
