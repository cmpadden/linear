# Contributing to Linear CLI

## Project Structure

The Linear CLI follows an entity-based architecture where code is organized by domain entities (issues, projects, teams, cycles, users, labels). This structure improves maintainability and makes it easy to find and modify code.

```
src/linear/
├── models/          # Pydantic data models
│   ├── __init__.py  # Re-exports all models
│   ├── base.py      # Shared models (PageInfo, Organization)
│   ├── issues.py    # Issue, WorkflowState, Comment, Attachment
│   ├── projects.py  # Project, ProjectConnection
│   ├── teams.py     # Team, TeamConnection
│   ├── cycles.py    # Cycle, CycleConnection
│   ├── users.py     # User, UserConnection
│   └── labels.py    # Label, LabelConnection
├── api/             # GraphQL API client methods
│   ├── __init__.py  # Unified LinearClient
│   ├── client.py    # Base client (LinearClient, LinearClientError)
│   ├── issues.py    # list_issues, search_issues, get_issue, create_issue
│   ├── projects.py  # list_projects, get_project
│   ├── teams.py     # list_teams, get_team
│   ├── cycles.py    # list_cycles, get_cycle
│   ├── users.py     # list_users, get_user, get_viewer
│   └── labels.py    # list_labels
├── formatters/      # Output formatting functions
│   ├── __init__.py  # Re-exports all formatters
│   ├── base.py      # Shared imports only
│   ├── issues.py    # format_table, format_table_grouped, format_json, format_issue_detail
│   ├── projects.py  # format_projects_table, format_project_detail, format_projects_json
│   ├── teams.py     # format_teams_table, format_team_detail, format_teams_json
│   ├── cycles.py    # format_cycles_table, format_cycle_detail, format_cycles_json
│   ├── users.py     # format_users_table, format_user_detail, format_users_json
│   └── labels.py    # format_labels_table, format_labels_json
├── commands/        # CLI command implementations
│   ├── __init__.py  # Exports all sub-apps
│   ├── issues.py    # Issues commands (list, view, search, create)
│   ├── projects.py  # Projects commands (list, view)
│   ├── teams.py     # Teams commands (list, view)
│   ├── cycles.py    # Cycles commands (list, view)
│   ├── users.py     # Users commands (list, view)
│   └── labels.py    # Labels commands (list)
├── __init__.py      # Package initialization and exports
├── cli.py           # Main CLI entry point (~67 lines)
└── claude_integration.py  # Claude AI helper functions
```

## Development Setup

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/linear-cli.git
   cd linear-cli
   ```

2. **Install dependencies** (using uv):
   ```bash
   uv sync
   ```

3. **Set up your API key**:
   ```bash
   export LINEAR_API_KEY="your_api_key_here"
   ```
   Get your API key at: https://linear.app/settings/api

4. **Run the CLI**:
   ```bash
   uv run linear --help
   ```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run code quality checks before commits. All hooks use `uv run` to execute tools from the project's virtual environment:
- `ruff check --fix` for linting
- `ruff format` for code formatting
- `ty check` for type checking

**Setup:**

```bash
# Install dev dependencies (includes pre-commit, ruff, and ty)
uv sync --dev

# Install the pre-commit hooks
uv run pre-commit install
```

**Manual run:**

```bash
# Run on all files
uv run pre-commit run --all-files

# Run on staged files only
uv run pre-commit run
```

The hooks will automatically run when you commit changes. If any issues are found and auto-fixed, you'll need to stage the fixes and commit again.

## Code Organization

### Entity-Based Architecture

The project follows an **entity-based architecture** where each Linear resource type (issue, project, team, cycle, user, label) has its own modules across all layers:

- **Models Layer**: Pydantic models for data validation and serialization
- **API Layer**: GraphQL client methods for interacting with the Linear API
- **Formatters Layer**: Output formatting functions (tables, JSON, detail views)
- **Commands Layer**: CLI command implementations using Typer

### Key Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Entity Cohesion**: All code for an entity lives in corresponding files across layers
3. **Explicit Imports**: Always use absolute imports (`from linear.models import Issue`)
4. **Re-export Pattern**: Package `__init__.py` files re-export symbols for clean imports

### File Size Guidelines

Keep individual files focused and manageable:
- **Models**: Aim for < 150 lines per entity
- **API Methods**: Aim for < 300 lines per entity
- **Formatters**: Aim for < 300 lines per entity
- **Commands**: Aim for < 200 lines per entity (issues.py is an exception due to AI integration)

If a file grows beyond these guidelines, consider splitting it further (e.g., separate creation/mutation methods).

## Adding New Features

### Adding a New Command to an Existing Entity

1. **Add the command function** in `commands/{entity}.py`:
   ```python
   @app.command("new-command")
   def new_command(
       option: str = typer.Option(..., help="Description"),
   ) -> None:
       """Command description."""
       try:
           client = LinearClient()
           # Implementation
       except LinearClientError as e:
           console.print(f"[red]Error: {e}[/red]")
           raise typer.Exit(1)
   ```

2. **Add formatter if needed** in `formatters/{entity}.py`:
   ```python
   def format_new_view(data: EntityType) -> None:
       """Format description."""
       console = Console()
       # Implementation
   ```

3. **Export formatter** in `formatters/__init__.py` if you added one

4. **Test the command**:
   ```bash
   uv run linear {entity} new-command --help
   uv run linear {entity} new-command --option value
   ```

### Adding a New API Method

1. **Add the method** in `api/{entity}.py`:
   ```python
   def new_method(
       self: "LinearClient",
       param: str,
   ) -> ReturnType:
       """Method description.

       Args:
           param: Parameter description

       Returns:
           Return value description

       Raises:
           LinearClientError: When the query fails
       """
       query = """
       query NewQuery($param: String!) {
         # GraphQL query
       }
       """

       variables = {"param": param}
       response = self.query(query, variables)

       try:
           return Model.model_validate(response["data"])
       except ValidationError as e:
           raise LinearClientError(f"Failed to parse: {e.errors()[0]['msg']}")
   ```

2. **Add method to LinearClient** in `api/__init__.py`:
   ```python
   class LinearClient(BaseClient):
       # ... existing methods ...
       new_method = entity.new_method
   ```

3. **Test the method**:
   ```python
   from linear.api import LinearClient

   client = LinearClient()
   result = client.new_method("test")
   ```

### Adding a New Entity Type

If Linear adds a new resource type (e.g., "Documents"):

1. **Create model** in `models/documents.py`:
   ```python
   """Document-related Pydantic models."""
   from pydantic import BaseModel, ConfigDict, Field
   from .base import PageInfo

   class Document(BaseModel):
       model_config = ConfigDict(populate_by_name=True)
       # Fields here

   class DocumentConnection(BaseModel):
       nodes: list[Document] = Field(default_factory=list)
       page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
   ```

2. **Export model** in `models/__init__.py`

3. **Create API methods** in `api/documents.py`

4. **Add methods to LinearClient** in `api/__init__.py`

5. **Create formatters** in `formatters/documents.py`

6. **Export formatters** in `formatters/__init__.py`

7. **Create commands** in `commands/documents.py`:
   ```python
   import typer
   from linear.api import LinearClient, LinearClientError
   from linear.formatters import format_documents_table

   app = typer.Typer(help="Manage Linear documents")

   @app.command("list")
   def list_documents() -> None:
       """List documents."""
       # Implementation
   ```

8. **Export commands sub-app** in `commands/__init__.py`

9. **Register sub-app** in `cli.py`:
   ```python
   from linear.commands import documents

   app.add_typer(documents.app, name="documents")
   ```

## Code Style and Standards

### Python Style

- **Python Version**: 3.11+
- **Type Hints**: Use type hints for all function parameters and return values
- **Formatting**: Use `ruff format` for code formatting
- **Linting**: Use `ruff check` for linting

### Import Organization

```python
"""Module docstring."""

# Standard library imports
import json
from typing import Any

# Third-party imports
from pydantic import BaseModel, Field
from rich.console import Console

# Local imports
from linear.models import Issue
from .base import something

# Forward references for type checking
if TYPE_CHECKING:
    from .client import LinearClient
```

### Naming Conventions

- **Functions/Methods**: `snake_case` (e.g., `list_issues`, `format_table`)
- **Classes**: `PascalCase` (e.g., `LinearClient`, `Issue`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_URL`, `RATE_LIMIT`)
- **Private**: Prefix with underscore (e.g., `_internal_method`)

### Documentation

- **Module docstrings**: Brief description at the top of each file
- **Function docstrings**: Google-style docstrings with Args, Returns, Raises sections
- **Inline comments**: Use sparingly, prefer self-documenting code

Example:
```python
def list_issues(
    self: "LinearClient",
    team: str | None = None,
    limit: int = 50,
) -> list[Issue]:
    """List issues with optional filters.

    Args:
        team: Filter by team key (e.g., ENG, DESIGN)
        limit: Maximum number of issues to return (default: 50)

    Returns:
        List of Issue objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # Implementation
```

### Error Handling

- **API Errors**: Always wrap API calls in try/except and catch `LinearClientError`
- **Validation Errors**: Catch `ValidationError` from Pydantic and provide helpful messages
- **CLI Errors**: Print errors in red using Rich and exit with code 1
- **Graceful Degradation**: Handle missing optional fields with sensible defaults

Example:
```python
try:
    client = LinearClient()
    issues = client.list_issues(team="ENG")
    format_table(issues)
except LinearClientError as e:
    console.print(f"[red]Error: {e}[/red]")
    raise typer.Exit(1)
```

### GraphQL Queries

- **Inline Queries**: Keep GraphQL queries inline in API methods (don't extract to separate files)
- **Field Selection**: Only request fields that are used
- **Consistent Formatting**: Use consistent indentation (2 spaces) in GraphQL queries
- **Comments**: Add comments for complex filter logic

## Testing

### Manual Testing

Test your changes with real API calls:

```bash
# Test basic functionality
uv run linear issues list --limit 3

# Test with filters
uv run linear issues list --team ENG --status "In Progress"

# Test error handling
uv run linear issues view INVALID-ID

# Test help text
uv run linear issues --help
```

### Import Testing

Verify imports work correctly:

```python
# Test model imports
from linear.models import Issue, Project, Team

# Test API imports
from linear.api import LinearClient, LinearClientError

# Test formatter imports
from linear.formatters import format_table, format_issue_detail
```

### Compilation Check

Ensure all Python files compile:

```bash
uv run python -m py_compile src/linear/**/*.py
```

## Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Test your changes** thoroughly:
   - Run manual tests with real API calls
   - Verify imports work correctly
   - Check compilation

4. **Update documentation** if needed:
   - Update README.md if adding new commands
   - Update this CONTRIBUTING.md if changing structure
   - Add docstrings to all new functions

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**:
   - Provide a clear title and description
   - Reference any related issues
   - Describe what was changed and why
   - Include testing steps

## Releases

This project uses GitHub Actions for automated PyPI publishing. When you create a GitHub release, the workflow automatically validates, builds, and publishes to PyPI.

### Setup

**For Repository Maintainers:**

1. Generate a PyPI API token at https://pypi.org/manage/account/token/
   - Scope: Project (`linear-app`)
   - Token name: `linear-app-github-actions`
2. Add the token to GitHub repository secrets:
   - Go to: Settings →  Secrets and variables →  Actions
   - Create new secret: `PYPI_API_TOKEN`

### Release Process

1. **Update version in pyproject.toml**
   ```bash
   vim pyproject.toml  # Change version = "X.Y.Z"
   ```

2. **Commit and push version bump**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

3. **Create GitHub release**

   **Option A: Using GitHub CLI (recommended)**
   ```bash
   gh release create vX.Y.Z --generate-notes
   ```

### Tag Format

Releases use the `vX.Y.Z` tag format (e.g., `v0.0.1`).

### CI/CD

- **Pull Requests & Main Branch**: CI workflow runs quality checks on all PRs and pushes to main
- **GitHub Releases**: Publish workflow automatically deploys to PyPI
- **Status Checks**: CI checks are required to pass before merging PRs
