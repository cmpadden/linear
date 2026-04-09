.PHONY: help install format lint ty check build test clean pre-commit ruff docs

help:
	@echo "Linear CLI - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install       Install dependencies (including dev dependencies)"
	@echo "  ty            Run ty type checker"
	@echo "  ruff          Format code with ruff"
	@echo "  check         Run all checks (format, lint, ty)"
	@echo "  docs          Generate CLI documentation (DOCUMENTATION.md)"
	@echo "  build         Build distributions (wheel + sdist)"
	@echo "  test          Run tests (placeholder)"
	@echo "  clean         Remove cache and build artifacts"
	@echo "  pre-commit    Install pre-commit hooks"
	@echo "  release-patch Create patch release (0.0.7 → 0.0.8)"
	@echo "  release-minor Create minor release (0.0.7 → 0.1.0)"
	@echo "  release-major Create major release (0.0.7 → 1.0.0)"

install:
	uv sync --dev

ruff:
	uv run ruff check --fix .
	uv run ruff format .

ty:
	uv run ty check

check: ruff ty
	@echo "✓ All checks passed"

docs:
	@uv run linear docs > DOCUMENTATION.md
	@echo "Successfully generated DOCUMENTATION.md"

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

build:
	@echo "Building distributions..."
	@rm -rf dist/
	@uv build
	@echo "Built distributions:"
	@ls -lh dist/

release-patch: check
	@./scripts/release.sh patch

release-minor: check
	@./scripts/release.sh minor

release-major: check
	@./scripts/release.sh major
