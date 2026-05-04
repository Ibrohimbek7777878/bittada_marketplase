# BITTADA — developer commands
# All commands run via Docker Compose so that dev parity matches prod.

.PHONY: help up down build logs ps shell migrate makemigrations \
        superuser test lint fmt typecheck seed reset frontend-dev

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start full stack (detached)
	docker compose up -d

down: ## Stop full stack
	docker compose down

build: ## Rebuild images
	docker compose build

logs: ## Tail logs
	docker compose logs -f --tail=200

ps: ## List containers
	docker compose ps

shell: ## Open Django shell
	docker compose exec backend python manage.py shell

migrate: ## Apply migrations
	docker compose exec backend python manage.py migrate

makemigrations: ## Create migrations
	docker compose exec backend python manage.py makemigrations

superuser: ## Create superuser
	docker compose exec backend python manage.py createsuperuser

test: ## Run pytest
	docker compose exec backend pytest -q

lint: ## Run ruff
	docker compose exec backend ruff check .

fmt: ## Auto-format with ruff + black
	docker compose exec backend ruff check --fix .
	docker compose exec backend black .

typecheck: ## Run mypy
	docker compose exec backend mypy apps core

seed: ## Load fixture data (dev only)
	docker compose exec backend python manage.py loaddata fixtures/dev_seed.json

reset: ## DANGER — drop volumes and rebuild
	docker compose down -v
	docker compose up -d --build

frontend-dev: ## Run Vite dev server (host)
	cd frontend && npm install && npm run dev
