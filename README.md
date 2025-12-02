<img width="1400" height="225" alt="linear-cli-header" src="https://github.com/user-attachments/assets/ce620de7-718d-4205-b4a0-bb287dc910a4" />

# Linear CLI

A command-line interface for interacting with [Linear](https://linear.app) - list issues, view project details, and manage your workflow from the terminal.

## Authentication

Set your Linear API key as an environment variable:

```bash
export LINEAR_API_KEY="<linear-api-key>"
```

Get your API key at: https://linear.app/settings/api

## Available Commands

### Issues

```bash
# List issues with filters
linear issues list [OPTIONS]

# Get details of a specific issue
linear issues get <issue-id>
```

**Common options:**
- `--assignee <email>` - Filter by assignee
- `--status <status>` - Filter by status (e.g., "in progress", "done")
- `--priority <0-4>` - Filter by priority
- `--team <team>` - Filter by team name or key
- `--project <name>` - Filter by project name
- `--label <label>` - Filter by label (repeatable)
- `--limit <n>` - Number of results (default: 50)
- `--format <format>` - Output format: `table` (default), `json`

### Projects

```bash
# List projects
linear projects list [OPTIONS]
```

**Common options:**
- `--state <state>` - Filter by state (planned, started, paused, completed, canceled)
- `--team <team>` - Filter by team name
- `--limit <n>` - Number of results (default: 50)
- `--format <format>` - Output format: `table` (default), `json`
