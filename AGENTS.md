# Agent Guidelines for Linear CLI

## Build/Test Commands
- **Install**: `uv sync --dev` (installs all dependencies including dev tools)
- **Format & Lint**: `make ruff` or `uv run ruff check --fix . && uv run ruff format .`
- **Type Check**: `make ty` or `uv run ty check`
- **Run All Checks**: `make check` (runs ruff + ty)
- **Run CLI**: `uv run linear --help`
- **No Tests**: Project has no test suite yet (`make test` is a placeholder)

## Code Style
- **Python**: 3.13+, use modern type hints (`str | None`, not `Optional[str]`)
- **Line Length**: 88 characters (enforced by ruff)
- **Quotes**: Double quotes (enforced by ruff)
- **Imports**: Standard library → third-party → local; use absolute imports (`from linear.models import Issue`)
- **Naming**: `snake_case` for functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Google-style with Args/Returns/Raises sections for all public functions

## Architecture
- **Entity-based**: Code organized by domain (issues, projects, teams, cycles, users, labels)
- **4 Layers**: models/ (Pydantic), api/ (GraphQL client), formatters/ (output), commands/ (CLI)
- **Re-exports**: Each layer's `__init__.py` re-exports symbols for clean imports
- **Error Handling**: Catch `LinearClientError` for API errors, `ValidationError` for data validation; print errors in red using Rich and exit with code 1

## Key Patterns
- **GraphQL Queries**: Inline in API methods (don't extract to files), 2-space indentation
- **CLI Commands**: Use Typer with rich type annotations; support `--format` flag (table/json)
- **Formatters**: Use Rich library for tables/colors; handle empty lists gracefully
- **Models**: Pydantic with `ConfigDict(populate_by_name=True)`; use Field aliases for camelCase GraphQL fields
