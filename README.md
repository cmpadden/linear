<img width="1400" height="225" src="https://github.com/user-attachments/assets/ce620de7-718d-4205-b4a0-bb287dc910a4" />

# Linear CLI

A command-line interface for interacting with [Linear](https://linear.app) - list issues, view project details, and manage your workflow from the terminal.

## Getting started

```bash
 $ LINEAR_API_KEY="<linear-api-key>" uvx --from linear-app linear

 Usage: linear [OPTIONS] COMMAND [ARGS]...

 Linear CLI - Interact with Linear from your terminal

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -v        Show version and exit                                                               │
│ --install-completion            Install completion for the current shell.                                           │
│ --show-completion               Show completion for the current shell, to copy it or customize the installation.    │
│ --help                          Show this message and exit.                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ issues     Manage Linear issues                                                                                     │
│ projects   Manage Linear projects                                                                                   │
│ teams      Manage Linear teams                                                                                      │
│ cycles     Manage Linear cycles                                                                                     │
│ users      Manage Linear users                                                                                      │
│ labels     Manage Linear labels                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Get your API key at: https://linear.app/settings/api

## Available Commands

### Issues

```bash
# List issues with filters
linear issues list [OPTIONS]

# View details of a specific issue
linear issues view <issue-id> [OPTIONS]

# Search issues by title
linear issues search <query> [OPTIONS]

# Create a new issue (natural language prompt or interactive)
linear issues create [prompt] [OPTIONS]
```

**List options:**
- `--assignee <email>` - Filter by assignee (use "me" or "self" for yourself)
- `--status <status>` - Filter by status (e.g., "in progress", "done")
- `--priority <0-4>` - Filter by priority
- `--team <team>` - Filter by team name or key
- `--project <name>` - Filter by project name
- `--label <label>` - Filter by label (repeatable)
- `--limit <n>` - Number of results (default: 50)
- `--sort <field>` - Sort results
- `--format <format>` - Output format: `table` (default), `json`

**View options:**
- `--web/-w` - Open issue in browser
- `--format/-f <format>` - Output format: `detail` (default), `json`

**Search options:**
- `--limit <n>` - Number of results (default: 50)
- `--sort <field>` - Sort results
- `--format/-f <format>` - Output format: `table` (default), `json`

**Create options:**
- `--title <text>` - Issue title (skips AI parsing, required for structured mode)
- `--team/-t <team>` - Team key (e.g., "ENG")
- `--description/-d <text>` - Issue description
- `--assignee/-a <email>` - Assign to user
- `--priority/-p <0-4>` - Priority level
- `--project <name>` - Project name
- `--label/-l <label>` - Add label (repeatable)
- `--format/-f <format>` - Output format: `detail` (default), `json`

### Projects

```bash
# List projects
linear projects list [OPTIONS]

# View details of a specific project
linear projects view <project-id> [OPTIONS]
```

**List options:**
- `--state <state>` - Filter by state (planned, started, paused, completed, canceled)
- `--team <team>` - Filter by team name or key
- `--limit <n>` - Number of results (default: 50)
- `--include-archived` - Include archived projects
- `--format/-f <format>` - Output format: `table` (default), `json`

**View options:**
- `--format/-f <format>` - Output format: `detail` (default), `json`

### Teams

```bash
# List all teams
linear teams list [OPTIONS]

# View details of a specific team
linear teams view <team-id> [OPTIONS]
```

**List options:**
- `--limit <n>` - Number of results (default: 50)
- `--include-archived` - Include archived teams
- `--format/-f <format>` - Output format: `table` (default), `json`

**View options:**
- `--format/-f <format>` - Output format: `detail` (default), `json`

Note: Team ID can be a team key (e.g., "ENG") or team ID.

### Cycles

```bash
# List cycles
linear cycles list [OPTIONS]

# View details of a specific cycle
linear cycles view <cycle-id> [OPTIONS]
```

**List options:**
- `--team/-t <team>` - Filter by team name or key
- `--active/-a` - Show only active cycles
- `--future` - Show only future cycles
- `--past` - Show only past cycles
- `--limit/-l <n>` - Number of results (default: 50)
- `--include-archived` - Include archived cycles
- `--format/-f <format>` - Output format: `table` (default), `json`

**View options:**
- `--format/-f <format>` - Output format: `detail` (default), `json`

### Users

```bash
# List workspace users
linear users list [OPTIONS]

# View details of a specific user
linear users view <user-id> [OPTIONS]
```

**List options:**
- `--active-only` - Show only active users (default: true)
- `--include-disabled` - Include disabled users
- `--limit/-l <n>` - Number of results (default: 50)
- `--format/-f <format>` - Output format: `table` (default), `json`

**View options:**
- `--format/-f <format>` - Output format: `detail` (default), `json`

Note: User ID can be an email address or user ID.

### Labels

```bash
# List issue labels
linear labels list [OPTIONS]
```

**List options:**
- `--team/-t <team>` - Filter by team ID or key
- `--limit/-l <n>` - Number of results (default: 50)
- `--include-archived` - Include archived labels
- `--format/-f <format>` - Output format: `table` (default), `json`

### Common Patterns

**Command Aliases:**
You can use short aliases for all command groups:
- `linear i` instead of `linear issues`
- `linear p` instead of `linear projects`
- `linear t` instead of `linear teams`
- `linear c` instead of `linear cycles`
- `linear u` instead of `linear users`
- `linear l` instead of `linear labels`

**Output Formats:**
- `table` - Human-readable table format (default for list commands)
- `json` - JSON output for scripting and automation
- `detail` - Detailed view (default for view commands)

**Common Flags:**
- Most list commands support `--limit` to control result count
- Most list commands support `--include-archived` to show archived items
- All commands support `--format/-f` to change output format

## Development

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
