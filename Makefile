.PHONY: help bootstrap bootstrap-demo test coverage lint check down reset clean

COMPOSE_DEV      := docker compose -f docker-compose.dev.yml
COMPOSE_PROD     := docker compose -f docker-compose.yml

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | awk -F':.*?##' '{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

bootstrap: ## build stack, run migrations, collectstatic (no demo data)
	@test -f .env || cp .env.example .env
	$(COMPOSE_DEV) up -d --build
	$(COMPOSE_DEV) exec -T web python manage.py migrate --noinput
	$(COMPOSE_DEV) exec -T web python manage.py collectstatic --noinput

bootstrap-demo: ## bootstrap and load demo accounts
	$(MAKE) bootstrap
	$(COMPOSE_DEV) exec -T web python manage.py load_demo_data

test: ## run pytest inside the dev container
	$(COMPOSE_DEV) exec -T web pytest

coverage: ## run pytest with coverage gate (>=80%)
	$(COMPOSE_DEV) exec -T web pytest --cov-report=term-missing

lint: ## flake8, black --check, isort --check
	$(COMPOSE_DEV) exec -T web sh -c 'flake8 . --max-line-length=120 --exclude=migrations,__pycache__,.venv,venv && black --check --line-length=120 . && isort --check-only --profile black .'

check: ## Django deployment system checks
	$(COMPOSE_DEV) exec -T web python manage.py check --deploy

down: ## stop dev stack
	$(COMPOSE_DEV) down

reset: down ## stop stack and drop volumes
	$(COMPOSE_DEV) down -v
