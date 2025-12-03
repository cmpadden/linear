.PHONY: help install format lint ty check test clean pre-commit ruff

help:
	@echo "Linear CLI - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install       Install dependencies (including dev dependencies)"
	@echo "  format        Format code with ruff"
	@echo "  lint          Run ruff linter with auto-fix"
	@echo "  ty            Run ty type checker"
	@echo "  check         Run all checks (format, lint, ty)"
	@echo "  test          Run tests (placeholder)"
	@echo "  clean         Remove cache and build artifacts"
	@echo "  pre-commit    Install pre-commit hooks"
	@echo "  ruff          Alias for format (legacy)"

install:
	uv sync --dev

format:
	uv run ruff format src/

lint:
	uv run ruff check --fix src/

ty:
	uv run ty check

check: format lint ty
	@echo "✓ All checks passed"

test:
	@echo "No tests configured yet"

clean:
	rm -rf .venv
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

pre-commit:
	uv run pre-commit install
	@echo "✓ Pre-commit hooks installed"

ruff: format
