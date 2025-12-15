.PHONY: help install install-dev clean test test-cov test-cov-html coverage lint format fix typecheck check all docker-up docker-down docker-logs docker-restart docker-clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  clean            Remove build artifacts and cache files"
	@echo "  test             Run all tests"
	@echo "  test-cov         Run tests with coverage report"
	@echo "  coverage         Alias for test-cov-html"
	@echo "  test-cov-html    Run tests with HTML coverage report"
	@echo "  lint             Run ruff linter (check only)"
	@echo "  format           Run ruff formatter (check only)"
	@echo "  fix              Auto-fix linting and formatting issues"
	@echo "  typecheck        Run mypy type checker"
	@echo "  check            Run all checks (lint, format, typecheck)"
	@echo "  all              Run all checks and tests with coverage"
	@echo "  docker-up        Start all Docker services"
	@echo "  docker-down      Stop and remove all Docker services"
	@echo "  docker-logs      View logs from all Docker services"
	@echo "  docker-restart   Restart all Docker services"
	@echo "  docker-clean     Stop services and remove volumes"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

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
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=term-missing -v

test-cov-html:
	pytest tests/ --cov=src --cov-report=html -v
	@echo "Coverage report generated in htmlcov/index.html"

# Alias for coverage
coverage: test-cov-html

# Linting and Formatting
lint:
	ruff check src/ tests/ simulator/

format:
	ruff format --check src/ tests/ simulator/

fix:
	ruff check --fix src/ tests/ simulator/
	ruff format src/ tests/ simulator/

# Type Checking
typecheck:
	mypy src/

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
