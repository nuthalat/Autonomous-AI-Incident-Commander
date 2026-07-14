.PHONY: help install install-dev lint format typecheck test test-cov run docker-up docker-down clean check

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PACKAGE := incident_commander

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in editable mode
	$(PIP) install -e .

install-dev: ## Install package with development dependencies
	$(PIP) install -e ".[dev]"

lint: ## Run Ruff linter
	ruff check .

format: ## Format code with Ruff
	ruff format .
	ruff check --fix .

typecheck: ## Run mypy on src
	mypy src

test: ## Run pytest
	pytest

test-cov: ## Run pytest with coverage
	pytest --cov=$(PACKAGE) --cov-report=term-missing

run: ## Start the API locally (uvicorn)
	uvicorn incident_commander.main:app --host 0.0.0.0 --port 8000 --reload

docker-up: ## Start dependencies and app via Docker Compose
	docker compose up --build -d

docker-down: ## Stop Docker Compose services
	docker compose down

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

check: lint typecheck test ## Run lint, typecheck, and tests
