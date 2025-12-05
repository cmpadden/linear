<img width="1400" height="225" src="https://github.com/user-attachments/assets/ce620de7-718d-4205-b4a0-bb287dc910a4" />

# Linear CLI

A command-line interface for interacting with [Linear](https://linear.app) - list issues, view project details, and manage your workflow from the terminal.

## Getting started

```bash
 $ export LINEAR_API_KEY="<linear-api-key>"  # https://linear.app/settings/api

 $ alias linear="uvx --from linear-app linear"

 $ linear issues create "Implement a views sub-command, assign to me on ENG team"

   Issue Summary:
     Title: Implement a views sub-command
     Description: Implement a views sub-command for the linear CLI
     Assignee: colton@acme.com
     Team: ENG
     Priority: None

   Create this issue? [y/n] (y):
```

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

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
