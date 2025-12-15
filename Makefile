.PHONY: help install install-dev clean test test-cov test-cov-html coverage test-integration test-integration-cov test-unit lint format fix typecheck check all docker-up docker-down docker-logs docker-restart docker-clean

# Python interpreter - use .venv if it exists, otherwise system python
PYTHON := $(shell if [ -d ".venv" ]; then echo ".venv/bin/python"; else echo "python"; fi)
PYTEST := $(shell if [ -d ".venv" ]; then echo ".venv/bin/pytest"; else echo "pytest"; fi)
RUFF := $(shell if [ -d ".venv" ]; then echo ".venv/bin/ruff"; else echo "ruff"; fi)
MYPY := $(shell if [ -d ".venv" ]; then echo ".venv/bin/mypy"; else echo "mypy"; fi)

# Default target
help:
	@echo "Available targets:"
	@echo "  install              Install production dependencies"
	@echo "  install-dev          Install development dependencies"
	@echo "  clean                Remove build artifacts and cache files"
	@echo "  test                 Run all tests"
	@echo "  test-unit            Run unit tests only (no Docker required)"
	@echo "  test-integration     Run integration tests (requires Docker)"
	@echo "  test-integration-cov Run integration tests with coverage"
	@echo "  test-cov             Run tests with coverage report"
	@echo "  coverage             Alias for test-cov-html"
	@echo "  test-cov-html        Run tests with HTML coverage report"
	@echo "  lint                 Run ruff linter (check only)"
	@echo "  format               Run ruff formatter (check only)"
	@echo "  fix                  Auto-fix linting and formatting issues"
	@echo "  typecheck            Run mypy type checker"
	@echo "  check                Run all checks (lint, format, typecheck)"
	@echo "  all                  Run all checks and tests with coverage"
	@echo "  docker-up            Start all Docker services"
	@echo "  docker-down          Stop and remove all Docker services"
	@echo "  docker-logs          View logs from all Docker services"
	@echo "  docker-restart       Restart all Docker services"
	@echo "  docker-clean         Stop services and remove volumes"

# Installation
install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

# Cleanup
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Testing
test:
	$(PYTEST) tests/ -v

test-unit:
	$(PYTEST) tests/ -v -m "not integration"
	@echo "✓ Unit tests completed (no Docker required)"

test-integration:
	@echo "Checking if Redis is running..."
	@docker ps --filter name=redis --filter status=running | grep redis > /dev/null || \
		(echo "❌ Redis not running. Start with: make docker-up" && exit 1)
	@echo "✓ Redis is running"
	$(PYTEST) tests/ -v -m integration
	@echo "✓ Integration tests completed"

test-integration-cov:
	@echo "Checking if Redis is running..."
	@docker ps --filter name=redis --filter status=running | grep redis > /dev/null || \
		(echo "❌ Redis not running. Start with: make docker-up" && exit 1)
	@echo "✓ Redis is running"
	$(PYTEST) tests/ -v -m integration --cov=src --cov-report=term-missing
	@echo "✓ Integration tests with coverage completed"

test-cov:
	$(PYTEST) tests/ --cov=src --cov-report=term-missing -v

test-cov-html:
	$(PYTEST) tests/ --cov=src --cov-report=html -v
	@echo "Coverage report generated in htmlcov/index.html"

# Alias for coverage
coverage: test-cov-html

# Linting and Formatting
lint:
	$(RUFF) check src/ tests/ simulator/

format:
	$(RUFF) format --check src/ tests/ simulator/

fix:
	$(RUFF) check --fix src/ tests/ simulator/
	$(RUFF) format src/ tests/ simulator/

# Type Checking
typecheck:
	$(MYPY) src/

# Combined Checks
check: lint format typecheck
	@echo "✓ All checks passed!"

all: check test-cov
	@echo "✓ All checks and tests passed!"

# Docker Commands
docker-up:
	docker-compose up -d
	@echo "✓ Docker services started"
	@echo "  Ingest API: http://localhost:8000"
	@echo "  Redis: localhost:6379"

docker-down:
	docker-compose down
	@echo "✓ Docker services stopped"

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart
	@echo "✓ Docker services restarted"

docker-clean:
	docker-compose down -v
	@echo "✓ Docker services stopped and volumes removed"
