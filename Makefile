.PHONY: help build up down logs test clean dev prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

logs-api: ## View API logs
	docker-compose logs -f api

logs-worker: ## View worker logs
	docker-compose logs -f worker

logs-db: ## View database logs
	docker-compose logs -f postgres

test: ## Run system tests
	python test_system.py

dev: ## Start development environment
	docker-compose up -d postgres mailhog
	uvicorn app.main:app --reload

dev-worker: ## Start development worker
	python -m app.worker

prod: ## Start production environment
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

install: ## Install Python dependencies
	pip install -r requirements.txt

db-reset: ## Reset database
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	docker-compose exec postgres psql -U quantalert -d quantalert -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

shell: ## Open shell in API container
	docker-compose exec api bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U quantalert -d quantalert

status: ## Show service status
	docker-compose ps
