.PHONY: help up down migrate test lint-imports contracts

help:
	@echo "RazorRecover AI - Monorepo Management Commands"
	@echo "  make up           Start all development containers"
	@echo "  make down         Stop all development containers"
	@echo "  make migrate      Run Alembic database migrations"
	@echo "  make test         Run backend unit & integration tests"
	@echo "  make lint-imports Enforce architectural layering import rules"
	@echo "  make contracts    Generate TypeScript contracts from FastAPI OpenAPI schema"

up:
	docker-compose up --build -d

down:
	docker-compose down

migrate:
	docker-compose exec api alembic upgrade head

test:
	pytest apps/api/tests

lint-imports:
	python apps/api/scripts/lint_imports.py

contracts:
	@echo "Generating OpenAPI contracts..."

eval:
	python apps/api/app/ai/evaluator.py
