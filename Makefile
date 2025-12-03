.PHONY: help install format lint ty check build publish test clean pre-commit ruff

help:
	@echo "Linear CLI - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install       Install dependencies (including dev dependencies)"
	@echo "  format        Format code with ruff"
	@echo "  lint          Run ruff linter with auto-fix"
	@echo "  ty            Run ty type checker"
	@echo "  check         Run all checks (format, lint, ty)"
	@echo "  build         Build distributions (wheel + sdist)"
	@echo "  publish       Complete release: check, build, publish, tag"
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

build:
	@echo "Building distributions..."
	@rm -rf dist/
	@uv build
	@echo "Built distributions:"
	@ls -lh dist/

publish: check
	@echo ""
	@echo "========================================"
	@echo "Publishing Linear CLI to PyPI"
	@echo "========================================"
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Version: $$VERSION"; \
	echo ""; \
	echo "Checking git status..."; \
	if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Working directory has uncommitted changes"; \
		exit 1; \
	fi; \
	echo "✓ Git working directory is clean"; \
	echo ""; \
	echo "Building distributions..."; \
	rm -rf dist/; \
	uv build; \
	echo ""; \
	echo "Built distributions:"; \
	ls -lh dist/; \
	echo ""; \
	read -p "Publish version $$VERSION to PyPI? (y/n) " -n 1 -r; \
	echo ""; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		echo "Publishing to PyPI..."; \
		uv publish; \
		echo ""; \
		echo "Creating and pushing git tag..."; \
		git tag "release-$$VERSION"; \
		git push origin "release-$$VERSION"; \
		echo ""; \
		echo "✓ Release $$VERSION completed successfully!"; \
		echo "View at: https://pypi.org/project/linear-app/$$VERSION/"; \
	else \
		echo "Publish cancelled"; \
		exit 1; \
	fi
