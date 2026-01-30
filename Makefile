# Makefile for common development tasks

.PHONY: help install dev test lint format type-check clean docs generate

help:
	@echo "Available commands:"
	@echo "  make install        Install package"
	@echo "  make dev            Install package with dev dependencies"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-int       Run integration tests only"
	@echo "  make lint           Lint code with ruff"
	@echo "  make format         Format code with ruff"
	@echo "  make type-check     Type check with mypy"
	@echo "  make clean          Clean build artifacts"
	@echo "  make docs           Build documentation"
	@echo "  make docs-serve     Serve documentation locally"
	@echo "  make generate       Regenerate code from OpenAPI spec"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-unit:
	pytest -m unit

test-int:
	pytest -m integration

test-cov:
	pytest --cov=rencom --cov-report=html --cov-report=term

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

type-check:
	mypy rencom/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && mkdocs build

docs-serve:
	cd docs && mkdocs serve

generate:
	python scripts/generate.py

build:
	python -m build

publish-test:
	python -m build
	twine upload --repository testpypi dist/*

publish:
	python -m build
	twine upload dist/*
