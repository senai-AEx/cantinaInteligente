PYTHON ?= python

.DEFAULT_GOAL := help
.PHONY: help setup up down db-up db-down migrate seed api web test status

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

web:
	@$(PYTHON) scripts/dev.py web

test:
	@$(PYTHON) scripts/dev.py test

status:
	@$(PYTHON) scripts/dev.py status
