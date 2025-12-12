.PHONY: help install install-dev clean test test-cov test-cov-html lint format fix typecheck check all

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  clean            Remove build artifacts and cache files"
	@echo "  test             Run all tests"
	@echo "  test-cov         Run tests with coverage report"
	@echo "  test-cov-html    Run tests with HTML coverage report"
	@echo "  lint             Run ruff linter (check only)"
	@echo "  format           Run ruff formatter (check only)"
	@echo "  fix              Auto-fix linting and formatting issues"
	@echo "  typecheck        Run mypy type checker"
	@echo "  check            Run all checks (lint, format, typecheck)"
	@echo "  all              Run all checks and tests with coverage"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-test.txt

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
