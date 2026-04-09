# Linear CLI Documentation

Linear CLI - Interact with Linear from your terminal

**Usage**:

```console
$ linear [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-V, --version`: Show version and exit
* `-v, --verbose`: Show verbose output (GraphQL queries, response times)
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `docs`: Generate comprehensive CLI documentation...
* `issues`: Manage Linear issues.
* `i`: Manage Linear issues.
* `attachments`: Manage issue attachments
* `comments`: Manage Linear comments
* `projects`: Manage Linear projects
* `p`: Manage Linear projects
* `teams`: Manage Linear teams
* `t`: Manage Linear teams
* `cycles`: Manage Linear cycles
* `c`: Manage Linear cycles
* `users`: Manage Linear users
* `u`: Manage Linear users
* `labels`: Manage Linear labels
* `l`: Manage Linear labels
* `roadmaps`: Manage Linear roadmaps
* `r`: Manage Linear roadmaps

## `linear docs`

Generate comprehensive CLI documentation in Markdown format to stdout.

**Usage**:

```console
$ linear docs [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `linear issues`

Manage Linear issues. Run &#x27;linear issues list&#x27; to see your assigned issues.

**Usage**:

```console
$ linear issues [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear issues.
* `view`: Get details of a specific Linear issue.
* `search`: Search Linear issues by title.
* `create`: Create a new Linear issue.
* `update`: Update an existing Linear issue.
* `delete`: Delete (trash) a Linear issue.
* `archive`: Archive a Linear issue.
* `unarchive`: Unarchive a Linear issue.
* `duplicate`: Duplicate an issue by creating a copy.
* `move-state`: Move an issue to a different workflow state.
* `relations`: Manage issue relations

### `linear issues list`

List Linear issues.

By default, shows issues assigned to you (like &quot;My Issues&quot; in Linear&#x27;s web app).
Use --all-assignees to see all issues, or --no-assignee to show only unassigned
issues.

Examples:

  # List your assigned issues (default)
  linear issues list

  # List unassigned issues
  linear issues list --no-assignee

  # List all issues in workspace
  linear issues list --all-assignees

  # List issues you created (manager view: see delegated work)
  linear issues list --creator me

  # List your team&#x27;s unassigned issues
  linear issues list --team ENG --no-assignee

  # List all issues in your team
  linear issues list --team ENG --all-assignees

  # List your assigned issues in a specific team
  linear issues list --team ENG

  # Filter by status
  linear issues list --status &quot;in progress&quot;

  # Explicitly filter by different assignee
  linear issues list --assignee user@example.com

  # Combine filters
  linear issues list --creator me --status &quot;in progress&quot;

  # Fetch all results
  linear issues list --all

  # Output as JSON
  linear issues list --format json

  # Filter by labels
  linear issues list --label bug --label urgent

**Usage**:

```console
$ linear issues list [OPTIONS]
```

**Options**:

* `-a, --assignee TEXT`: Filter by assignee email (use &#x27;me&#x27; or &#x27;self&#x27; for yourself)
* `-c, --creator TEXT`: Filter by issue creator email (use &#x27;me&#x27; or &#x27;self&#x27; for yourself)
* `--no-assignee`: Filter to unassigned issues
* `--all-assignees`: Show issues regardless of assignee (disable default &#x27;my issues&#x27; filter)
* `-p, --project TEXT`: Filter by project name
* `-s, --status TEXT`: Filter by status
* `-t, --team TEXT`: Filter by team key (e.g., ENG, DESIGN)
* `--priority INTEGER`: Filter by priority (0-4)
* `-l, --label TEXT`: Filter by label (repeatable)
* `--created-after TEXT`: Show issues created after date (YYYY-MM-DD)
* `--created-before TEXT`: Show issues created before date (YYYY-MM-DD)
* `--updated-after TEXT`: Show issues updated after date (YYYY-MM-DD)
* `--updated-before TEXT`: Show issues updated before date (YYYY-MM-DD)
* `--filter TEXT`: Complex filter query (e.g., &quot;team:ENG OR team:DESIGN AND priority:1&quot;)
* `--per-page INTEGER`: Number of issues per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived issues
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated, priority  [default: updated]
* `--group-by TEXT`: Group by: cycle, project, team (default: cycle)  [default: cycle]
* `--help`: Show this message and exit.

### `linear issues view`

Get details of a specific Linear issue.

Examples:

  # View issue by identifier
  linear issues view ENG-123

  # Open issue in browser
  linear issues view ENG-123 --web

   # View issue as JSON
   linear issues view ENG-123 --format json

**Usage**:

```console
$ linear issues view [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `-w, --web`: Open issue in web browser
* `--help`: Show this message and exit.

### `linear issues search`

Search Linear issues by title.

Examples:

  # Search for issues with &quot;authentication&quot; in title
  linear issues search authentication

  # Search with output as JSON
  linear issues search &quot;bug fix&quot; --format json

  # Fetch all matching results
  linear issues search refactor --all

  # Limit results per page
  linear issues search bug --per-page 10

**Usage**:

```console
$ linear issues search [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: Search query (searches issue titles and descriptions)  [required]

**Options**:

* `-a, --assignee TEXT`: Filter by assignee email
* `-c, --creator TEXT`: Filter by issue creator email
* `-p, --project TEXT`: Filter by project name
* `-s, --status TEXT`: Filter by status
* `-t, --team TEXT`: Filter by team key
* `--priority INTEGER`: Filter by priority (0-4)
* `-l, --label TEXT`: Filter by label (repeatable)
* `--created-after TEXT`: Show issues created after date (YYYY-MM-DD)
* `--created-before TEXT`: Show issues created before date (YYYY-MM-DD)
* `--updated-after TEXT`: Show issues updated after date (YYYY-MM-DD)
* `--updated-before TEXT`: Show issues updated before date (YYYY-MM-DD)
* `--filter TEXT`: Complex filter query (e.g., &quot;team:ENG OR team:DESIGN AND priority:1&quot;)
* `--per-page INTEGER`: Number of issues per page (max 250)  [default: 50]
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived issues
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated, priority  [default: updated]
* `--group-by TEXT`: Group by: cycle, project, team
* `--help`: Show this message and exit.

### `linear issues create`

Create a new Linear issue.


# Natural language with AI parsing (requires claude CLI)
linear issues create &quot;High priority bug to fix login for john@example.com in ENG team&quot;

# Structured mode with explicit --title (skips AI)
linear issues create --title &quot;Fix login bug&quot; --team ENG

# Structured mode with all options
linear issues create --title &quot;Add dark mode&quot; --team ENG --description &quot;Support dark theme&quot; --priority 2 --label feature --label ui

# Defaults: assignee=current user, team=auto-selected if only 1, priority=none

**Usage**:

```console
$ linear issues create [OPTIONS] [PROMPT]
```

**Arguments**:

* `[PROMPT]`: Natural language prompt describing the issue

**Options**:

* `--title TEXT`: Issue title (skips AI parsing)
* `-t, --team TEXT`: Team ID or key
* `-d, --description TEXT`: Issue description
* `-a, --assignee TEXT`: Assignee email (defaults to you)
* `-p, --priority INTEGER`: Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
* `--project TEXT`: Project ID or name
* `-l, --label TEXT`: Label name (repeatable)
* `-s, --state TEXT`: Workflow state name
* `-e, --estimate INTEGER`: Story points estimate
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear issues update`

Update an existing Linear issue.

Supports two modes:


1. CLI flags (update specific fields):
   linear issues update ENG-123 --title &quot;New title&quot; --priority 2


2. Interactive editor (edit all fields in $EDITOR):
   linear issues update ENG-123


The command will show a before/after comparison and ask for confirmation
before applying changes. Only specified fields are updated; all other
fields remain unchanged.


Examples:
  # Update title and priority
  linear issues update ENG-123 --title &quot;Fix login bug&quot; --priority 1

  # Reassign to yourself
  linear issues update ENG-123 --assignee me

  # Unassign issue
  linear issues update ENG-123 --assignee null

  # Clear estimate
  linear issues update ENG-123 --estimate -1

  # Update multiple labels (replaces all)
  linear issues update ENG-123 --label bug --label urgent

  # Open in editor for interactive editing
  linear issues update ENG-123

   # Output as JSON
   linear issues update ENG-123 --title &quot;New title&quot; --format json

**Usage**:

```console
$ linear issues update [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `--title TEXT`: New issue title
* `-d, --description TEXT`: New issue description
* `-a, --assignee TEXT`: Assignee email (use &#x27;me&#x27; for yourself, &#x27;null&#x27; to unassign)
* `-p, --priority INTEGER`: Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
* `--project TEXT`: Project ID or name (use &#x27;null&#x27; to remove)
* `-l, --label TEXT`: Label name (repeatable, replaces all labels)
* `-s, --state TEXT`: Workflow state name
* `-e, --estimate INTEGER`: Story points estimate (use -1 to clear)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear issues delete`

Delete (trash) a Linear issue.

Examples:

  # Delete an issue with confirmation
  linear issues delete ENG-123

  # Delete without confirmation prompt
  linear issues delete ENG-123 --yes

**Usage**:

```console
$ linear issues delete [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear issues archive`

Archive a Linear issue.

Examples:

  # Archive an issue with confirmation
  linear issues archive ENG-123

  # Archive without confirmation prompt
  linear issues archive ENG-123 --yes

**Usage**:

```console
$ linear issues archive [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear issues unarchive`

Unarchive a Linear issue.

Examples:

  # Unarchive an issue with confirmation
  linear issues unarchive ENG-123

  # Unarchive without confirmation prompt
  linear issues unarchive ENG-123 --yes

**Usage**:

```console
$ linear issues unarchive [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear issues duplicate`

Duplicate an issue by creating a copy.

Creates a new issue with the same fields as the source issue (title, description,
priority, labels, project, state, estimate, due date). The new issue will be
unassigned. Use --link to also create a duplicate relation.

Examples:

  # Duplicate an issue with confirmation
  linear issues duplicate ENG-123

  # Duplicate without confirmation
  linear issues duplicate ENG-123 --yes

  # Duplicate and create a relation link
  linear issues duplicate ENG-123 --link --yes

  # Duplicate and show as JSON
  linear issues duplicate abc123-uuid --format json

**Usage**:

```console
$ linear issues duplicate [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier to duplicate  [required]

**Options**:

* `-y, --yes`: Skip confirmation
* `--link`: Create duplicate relation between issues
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear issues move-state`

Move an issue to a different workflow state.

Examples:

  # Move issue to &quot;In Progress&quot; state
  linear issues move-state ENG-123 &quot;In Progress&quot;

  # Move issue to &quot;Done&quot; state without confirmation
  linear issues move-state ENG-123 Done --yes

**Usage**:

```console
$ linear issues move-state [OPTIONS] ISSUE_ID STATE
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `STATE`: State name (e.g., &#x27;In Progress&#x27;, &#x27;Done&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear issues relations`

Manage issue relations

**Usage**:

```console
$ linear issues relations [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all relations for an issue.
* `add`: Add a relation between two issues.
* `remove`: Remove a relation from an issue.

#### `linear issues relations list`

List all relations for an issue.

Examples:

  # List relations for an issue
  linear issues relations list ENG-123

  # Output as JSON
  linear issues relations list ENG-123 --format json

**Usage**:

```console
$ linear issues relations list [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

#### `linear issues relations add`

Add a relation between two issues.

Examples:

  # Add a &#x27;related&#x27; relation
  linear issues relations add ENG-123 ENG-456

  # Add a &#x27;blocks&#x27; relation
  linear issues relations add ENG-123 ENG-456 --type blocks

  # Add a &#x27;blocked&#x27; relation
  linear issues relations add ENG-123 ENG-456 --type blocked

  # Add a &#x27;duplicate&#x27; relation
  linear issues relations add ENG-123 ENG-456 --type duplicate

**Usage**:

```console
$ linear issues relations add [OPTIONS] ISSUE_ID RELATED_ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Source issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `RELATED_ISSUE_ID`: Related issue ID or identifier (e.g., &#x27;ENG-456&#x27;)  [required]

**Options**:

* `-t, --type TEXT`: Relation type: blocks, blocked, related, duplicate  [default: related]
* `--help`: Show this message and exit.

#### `linear issues relations remove`

Remove a relation from an issue.

Use &#x27;linear issues relations list &lt;issue-id&gt;&#x27; to find relation IDs.

Examples:

  # Remove a relation
  linear issues relations remove ENG-123 &lt;relation-id&gt;

  # Remove without confirmation
  linear issues relations remove ENG-123 &lt;relation-id&gt; --yes

**Usage**:

```console
$ linear issues relations remove [OPTIONS] ISSUE_ID RELATION_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `RELATION_ID`: Relation ID to remove (use &#x27;list&#x27; to see IDs)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear i`

Manage Linear issues. Run &#x27;linear issues list&#x27; to see your assigned issues.

**Usage**:

```console
$ linear i [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear issues.
* `view`: Get details of a specific Linear issue.
* `search`: Search Linear issues by title.
* `create`: Create a new Linear issue.
* `update`: Update an existing Linear issue.
* `delete`: Delete (trash) a Linear issue.
* `archive`: Archive a Linear issue.
* `unarchive`: Unarchive a Linear issue.
* `duplicate`: Duplicate an issue by creating a copy.
* `move-state`: Move an issue to a different workflow state.
* `relations`: Manage issue relations

### `linear i list`

List Linear issues.

By default, shows issues assigned to you (like &quot;My Issues&quot; in Linear&#x27;s web app).
Use --all-assignees to see all issues, or --no-assignee to show only unassigned
issues.

Examples:

  # List your assigned issues (default)
  linear issues list

  # List unassigned issues
  linear issues list --no-assignee

  # List all issues in workspace
  linear issues list --all-assignees

  # List issues you created (manager view: see delegated work)
  linear issues list --creator me

  # List your team&#x27;s unassigned issues
  linear issues list --team ENG --no-assignee

  # List all issues in your team
  linear issues list --team ENG --all-assignees

  # List your assigned issues in a specific team
  linear issues list --team ENG

  # Filter by status
  linear issues list --status &quot;in progress&quot;

  # Explicitly filter by different assignee
  linear issues list --assignee user@example.com

  # Combine filters
  linear issues list --creator me --status &quot;in progress&quot;

  # Fetch all results
  linear issues list --all

  # Output as JSON
  linear issues list --format json

  # Filter by labels
  linear issues list --label bug --label urgent

**Usage**:

```console
$ linear i list [OPTIONS]
```

**Options**:

* `-a, --assignee TEXT`: Filter by assignee email (use &#x27;me&#x27; or &#x27;self&#x27; for yourself)
* `-c, --creator TEXT`: Filter by issue creator email (use &#x27;me&#x27; or &#x27;self&#x27; for yourself)
* `--no-assignee`: Filter to unassigned issues
* `--all-assignees`: Show issues regardless of assignee (disable default &#x27;my issues&#x27; filter)
* `-p, --project TEXT`: Filter by project name
* `-s, --status TEXT`: Filter by status
* `-t, --team TEXT`: Filter by team key (e.g., ENG, DESIGN)
* `--priority INTEGER`: Filter by priority (0-4)
* `-l, --label TEXT`: Filter by label (repeatable)
* `--created-after TEXT`: Show issues created after date (YYYY-MM-DD)
* `--created-before TEXT`: Show issues created before date (YYYY-MM-DD)
* `--updated-after TEXT`: Show issues updated after date (YYYY-MM-DD)
* `--updated-before TEXT`: Show issues updated before date (YYYY-MM-DD)
* `--filter TEXT`: Complex filter query (e.g., &quot;team:ENG OR team:DESIGN AND priority:1&quot;)
* `--per-page INTEGER`: Number of issues per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived issues
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated, priority  [default: updated]
* `--group-by TEXT`: Group by: cycle, project, team (default: cycle)  [default: cycle]
* `--help`: Show this message and exit.

### `linear i view`

Get details of a specific Linear issue.

Examples:

  # View issue by identifier
  linear issues view ENG-123

  # Open issue in browser
  linear issues view ENG-123 --web

   # View issue as JSON
   linear issues view ENG-123 --format json

**Usage**:

```console
$ linear i view [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `-w, --web`: Open issue in web browser
* `--help`: Show this message and exit.

### `linear i search`

Search Linear issues by title.

Examples:

  # Search for issues with &quot;authentication&quot; in title
  linear issues search authentication

  # Search with output as JSON
  linear issues search &quot;bug fix&quot; --format json

  # Fetch all matching results
  linear issues search refactor --all

  # Limit results per page
  linear issues search bug --per-page 10

**Usage**:

```console
$ linear i search [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: Search query (searches issue titles and descriptions)  [required]

**Options**:

* `-a, --assignee TEXT`: Filter by assignee email
* `-c, --creator TEXT`: Filter by issue creator email
* `-p, --project TEXT`: Filter by project name
* `-s, --status TEXT`: Filter by status
* `-t, --team TEXT`: Filter by team key
* `--priority INTEGER`: Filter by priority (0-4)
* `-l, --label TEXT`: Filter by label (repeatable)
* `--created-after TEXT`: Show issues created after date (YYYY-MM-DD)
* `--created-before TEXT`: Show issues created before date (YYYY-MM-DD)
* `--updated-after TEXT`: Show issues updated after date (YYYY-MM-DD)
* `--updated-before TEXT`: Show issues updated before date (YYYY-MM-DD)
* `--filter TEXT`: Complex filter query (e.g., &quot;team:ENG OR team:DESIGN AND priority:1&quot;)
* `--per-page INTEGER`: Number of issues per page (max 250)  [default: 50]
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived issues
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated, priority  [default: updated]
* `--group-by TEXT`: Group by: cycle, project, team
* `--help`: Show this message and exit.

### `linear i create`

Create a new Linear issue.


# Natural language with AI parsing (requires claude CLI)
linear issues create &quot;High priority bug to fix login for john@example.com in ENG team&quot;

# Structured mode with explicit --title (skips AI)
linear issues create --title &quot;Fix login bug&quot; --team ENG

# Structured mode with all options
linear issues create --title &quot;Add dark mode&quot; --team ENG --description &quot;Support dark theme&quot; --priority 2 --label feature --label ui

# Defaults: assignee=current user, team=auto-selected if only 1, priority=none

**Usage**:

```console
$ linear i create [OPTIONS] [PROMPT]
```

**Arguments**:

* `[PROMPT]`: Natural language prompt describing the issue

**Options**:

* `--title TEXT`: Issue title (skips AI parsing)
* `-t, --team TEXT`: Team ID or key
* `-d, --description TEXT`: Issue description
* `-a, --assignee TEXT`: Assignee email (defaults to you)
* `-p, --priority INTEGER`: Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
* `--project TEXT`: Project ID or name
* `-l, --label TEXT`: Label name (repeatable)
* `-s, --state TEXT`: Workflow state name
* `-e, --estimate INTEGER`: Story points estimate
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear i update`

Update an existing Linear issue.

Supports two modes:


1. CLI flags (update specific fields):
   linear issues update ENG-123 --title &quot;New title&quot; --priority 2


2. Interactive editor (edit all fields in $EDITOR):
   linear issues update ENG-123


The command will show a before/after comparison and ask for confirmation
before applying changes. Only specified fields are updated; all other
fields remain unchanged.


Examples:
  # Update title and priority
  linear issues update ENG-123 --title &quot;Fix login bug&quot; --priority 1

  # Reassign to yourself
  linear issues update ENG-123 --assignee me

  # Unassign issue
  linear issues update ENG-123 --assignee null

  # Clear estimate
  linear issues update ENG-123 --estimate -1

  # Update multiple labels (replaces all)
  linear issues update ENG-123 --label bug --label urgent

  # Open in editor for interactive editing
  linear issues update ENG-123

   # Output as JSON
   linear issues update ENG-123 --title &quot;New title&quot; --format json

**Usage**:

```console
$ linear i update [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `--title TEXT`: New issue title
* `-d, --description TEXT`: New issue description
* `-a, --assignee TEXT`: Assignee email (use &#x27;me&#x27; for yourself, &#x27;null&#x27; to unassign)
* `-p, --priority INTEGER`: Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
* `--project TEXT`: Project ID or name (use &#x27;null&#x27; to remove)
* `-l, --label TEXT`: Label name (repeatable, replaces all labels)
* `-s, --state TEXT`: Workflow state name
* `-e, --estimate INTEGER`: Story points estimate (use -1 to clear)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear i delete`

Delete (trash) a Linear issue.

Examples:

  # Delete an issue with confirmation
  linear issues delete ENG-123

  # Delete without confirmation prompt
  linear issues delete ENG-123 --yes

**Usage**:

```console
$ linear i delete [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear i archive`

Archive a Linear issue.

Examples:

  # Archive an issue with confirmation
  linear issues archive ENG-123

  # Archive without confirmation prompt
  linear issues archive ENG-123 --yes

**Usage**:

```console
$ linear i archive [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear i unarchive`

Unarchive a Linear issue.

Examples:

  # Unarchive an issue with confirmation
  linear issues unarchive ENG-123

  # Unarchive without confirmation prompt
  linear issues unarchive ENG-123 --yes

**Usage**:

```console
$ linear i unarchive [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear i duplicate`

Duplicate an issue by creating a copy.

Creates a new issue with the same fields as the source issue (title, description,
priority, labels, project, state, estimate, due date). The new issue will be
unassigned. Use --link to also create a duplicate relation.

Examples:

  # Duplicate an issue with confirmation
  linear issues duplicate ENG-123

  # Duplicate without confirmation
  linear issues duplicate ENG-123 --yes

  # Duplicate and create a relation link
  linear issues duplicate ENG-123 --link --yes

  # Duplicate and show as JSON
  linear issues duplicate abc123-uuid --format json

**Usage**:

```console
$ linear i duplicate [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier to duplicate  [required]

**Options**:

* `-y, --yes`: Skip confirmation
* `--link`: Create duplicate relation between issues
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear i move-state`

Move an issue to a different workflow state.

Examples:

  # Move issue to &quot;In Progress&quot; state
  linear issues move-state ENG-123 &quot;In Progress&quot;

  # Move issue to &quot;Done&quot; state without confirmation
  linear issues move-state ENG-123 Done --yes

**Usage**:

```console
$ linear i move-state [OPTIONS] ISSUE_ID STATE
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `STATE`: State name (e.g., &#x27;In Progress&#x27;, &#x27;Done&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear i relations`

Manage issue relations

**Usage**:

```console
$ linear i relations [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all relations for an issue.
* `add`: Add a relation between two issues.
* `remove`: Remove a relation from an issue.

#### `linear i relations list`

List all relations for an issue.

Examples:

  # List relations for an issue
  linear issues relations list ENG-123

  # Output as JSON
  linear issues relations list ENG-123 --format json

**Usage**:

```console
$ linear i relations list [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

#### `linear i relations add`

Add a relation between two issues.

Examples:

  # Add a &#x27;related&#x27; relation
  linear issues relations add ENG-123 ENG-456

  # Add a &#x27;blocks&#x27; relation
  linear issues relations add ENG-123 ENG-456 --type blocks

  # Add a &#x27;blocked&#x27; relation
  linear issues relations add ENG-123 ENG-456 --type blocked

  # Add a &#x27;duplicate&#x27; relation
  linear issues relations add ENG-123 ENG-456 --type duplicate

**Usage**:

```console
$ linear i relations add [OPTIONS] ISSUE_ID RELATED_ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Source issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `RELATED_ISSUE_ID`: Related issue ID or identifier (e.g., &#x27;ENG-456&#x27;)  [required]

**Options**:

* `-t, --type TEXT`: Relation type: blocks, blocked, related, duplicate  [default: related]
* `--help`: Show this message and exit.

#### `linear i relations remove`

Remove a relation from an issue.

Use &#x27;linear issues relations list &lt;issue-id&gt;&#x27; to find relation IDs.

Examples:

  # Remove a relation
  linear issues relations remove ENG-123 &lt;relation-id&gt;

  # Remove without confirmation
  linear issues relations remove ENG-123 &lt;relation-id&gt; --yes

**Usage**:

```console
$ linear i relations remove [OPTIONS] ISSUE_ID RELATION_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `RELATION_ID`: Relation ID to remove (use &#x27;list&#x27; to see IDs)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear attachments`

Manage issue attachments

**Usage**:

```console
$ linear attachments [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all attachments for an issue.
* `upload`: Upload a file attachment to an issue.
* `delete`: Delete an attachment.

### `linear attachments list`

List all attachments for an issue.

Examples:

  # List attachments for an issue
  linear attachments list ENG-123

  # Output as JSON
  linear attachments list ENG-123 --format json

**Usage**:

```console
$ linear attachments list [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear attachments upload`

Upload a file attachment to an issue.

Examples:

  # Upload a file
  linear attachments upload ENG-123 ./screenshot.png

  # Upload with custom title
  linear attachments upload ENG-123 ./doc.pdf --title &quot;Design Document&quot;

**Usage**:

```console
$ linear attachments upload [OPTIONS] ISSUE_ID FILE_PATH
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]
* `FILE_PATH`: Path to file to upload  [required]

**Options**:

* `-t, --title TEXT`: Attachment title (defaults to filename)
* `--help`: Show this message and exit.

### `linear attachments delete`

Delete an attachment.

Examples:

  # Delete an attachment with confirmation
  linear attachments delete &lt;attachment-id&gt;

  # Delete without confirmation prompt
  linear attachments delete &lt;attachment-id&gt; --yes

**Usage**:

```console
$ linear attachments delete [OPTIONS] ATTACHMENT_ID
```

**Arguments**:

* `ATTACHMENT_ID`: Attachment ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear comments`

Manage Linear comments

**Usage**:

```console
$ linear comments [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List comments on an issue.
* `create`: Add a comment to an issue.
* `update`: Update a comment.
* `delete`: Delete a comment.

### `linear comments list`

List comments on an issue.

Examples:

  # List comments on an issue
  linear comments list ENG-123

  # Output as JSON
  linear comments list ENG-123 --format json

**Usage**:

```console
$ linear comments list [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear comments create`

Add a comment to an issue.

If --body is not provided, opens your $EDITOR to write the comment.

Examples:

  # Create comment with body flag
  linear comments create ENG-123 --body &quot;This looks good!&quot;

  # Open editor to write comment
  linear comments create ENG-123

  # Output as JSON
  linear comments create ENG-123 --body &quot;Comment&quot; --format json

**Usage**:

```console
$ linear comments create [OPTIONS] ISSUE_ID
```

**Arguments**:

* `ISSUE_ID`: Issue ID or identifier (e.g., &#x27;ENG-123&#x27;)  [required]

**Options**:

* `-b, --body TEXT`: Comment body (markdown)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear comments update`

Update a comment.

If --body is not provided, opens your $EDITOR to edit the comment.

Examples:

  # Update comment with body flag
  linear comments update &lt;comment-id&gt; --body &quot;Updated text&quot;

  # Open editor to edit comment
  linear comments update &lt;comment-id&gt;

  # Output as JSON
  linear comments update &lt;comment-id&gt; --body &quot;Text&quot; --format json

**Usage**:

```console
$ linear comments update [OPTIONS] COMMENT_ID
```

**Arguments**:

* `COMMENT_ID`: Comment ID (UUID)  [required]

**Options**:

* `-b, --body TEXT`: New comment body (markdown)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear comments delete`

Delete a comment.

Examples:

  # Delete comment with confirmation
  linear comments delete &lt;comment-id&gt;

  # Delete without confirmation prompt
  linear comments delete &lt;comment-id&gt; --yes

**Usage**:

```console
$ linear comments delete [OPTIONS] COMMENT_ID
```

**Arguments**:

* `COMMENT_ID`: Comment ID (UUID)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear projects`

Manage Linear projects

**Usage**:

```console
$ linear projects [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear projects with optional filters.
* `view`: Get details of a specific Linear project.
* `create`: Create a new Linear project.
* `update`: Update an existing Linear project.
* `delete`: Delete a Linear project.
* `archive`: Archive a Linear project.
* `unarchive`: Unarchive a Linear project.

### `linear projects list`

List Linear projects with optional filters.

Examples:

  # List all projects
  linear projects list

  # Filter by state
  linear projects list --state started

  # Filter by team
  linear projects list --team engineering

  # Fetch all results
  linear projects list --all

  # Pagination
  linear projects list --page 2 --per-page 25

  # Output as JSON
  linear projects list --format json

**Usage**:

```console
$ linear projects list [OPTIONS]
```

**Options**:

* `-s, --state TEXT`: Filter by state (planned, started, paused, completed, canceled)
* `-t, --team TEXT`: Filter by team key (e.g., ENG, DESIGN)
* `--per-page INTEGER`: Number of projects per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived projects
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated  [default: updated]
* `--help`: Show this message and exit.

### `linear projects view`

Get details of a specific Linear project.

Examples:

  # View project by ID
  linear projects view abc123-def456

   # View project as JSON
   linear projects view my-project --format json

**Usage**:

```console
$ linear projects view [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear projects create`

Create a new Linear project.

Examples:

  # Create a project with minimal fields
  linear projects create --name &quot;Q1 Initiative&quot; --team ENG

  # Create with multiple teams
  linear projects create --name &quot;Cross-team Project&quot; --team ENG --team DESIGN

  # Create with all fields
  linear projects create --name &quot;Q1 Initiative&quot; --team ENG           --description &quot;Focus area&quot; --state started           --target-date 2026-03-31 --lead user@example.com

**Usage**:

```console
$ linear projects create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Project name (required)  [required]
* `-t, --team TEXT`: Team ID or key (can be used multiple times, required)  [required]
* `-d, --description TEXT`: Project description
* `-l, --lead TEXT`: Project lead (user email or ID)
* `--state TEXT`: Project state (planned, started, paused, completed, canceled)
* `--start-date TEXT`: Start date (YYYY-MM-DD)
* `--target-date TEXT`: Target date (YYYY-MM-DD)
* `--color TEXT`: Hex color code
* `--icon TEXT`: Icon name
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear projects update`

Update an existing Linear project.

Examples:

  # Update project name
  linear projects update my-project --name &quot;New Name&quot;

  # Update multiple fields
  linear projects update my-project --name &quot;New Name&quot; --state completed

  # Update teams (replaces all teams)
  linear projects update my-project --team ENG --team PLATFORM

**Usage**:

```console
$ linear projects update [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-n, --name TEXT`: New project name
* `-d, --description TEXT`: New project description
* `-t, --team TEXT`: Team ID or key (can be used multiple times, replaces all teams)
* `-l, --lead TEXT`: New project lead (user email or ID)
* `--state TEXT`: New project state (planned, started, paused, completed, canceled)
* `--start-date TEXT`: New start date (YYYY-MM-DD)
* `--target-date TEXT`: New target date (YYYY-MM-DD)
* `--color TEXT`: New hex color code
* `--icon TEXT`: New icon name
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear projects delete`

Delete a Linear project.

Examples:

  # Delete project (with confirmation)
  linear projects delete my-project

  # Delete without confirmation
  linear projects delete my-project --yes

**Usage**:

```console
$ linear projects delete [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear projects archive`

Archive a Linear project.

Examples:

  # Archive project (with confirmation)
  linear projects archive my-project

  # Archive without confirmation
  linear projects archive my-project --yes

**Usage**:

```console
$ linear projects archive [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear projects unarchive`

Unarchive a Linear project.

Examples:

  # Unarchive project (with confirmation)
  linear projects unarchive my-project

  # Unarchive without confirmation
  linear projects unarchive my-project --yes

**Usage**:

```console
$ linear projects unarchive [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear p`

Manage Linear projects

**Usage**:

```console
$ linear p [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear projects with optional filters.
* `view`: Get details of a specific Linear project.
* `create`: Create a new Linear project.
* `update`: Update an existing Linear project.
* `delete`: Delete a Linear project.
* `archive`: Archive a Linear project.
* `unarchive`: Unarchive a Linear project.

### `linear p list`

List Linear projects with optional filters.

Examples:

  # List all projects
  linear projects list

  # Filter by state
  linear projects list --state started

  # Filter by team
  linear projects list --team engineering

  # Fetch all results
  linear projects list --all

  # Pagination
  linear projects list --page 2 --per-page 25

  # Output as JSON
  linear projects list --format json

**Usage**:

```console
$ linear p list [OPTIONS]
```

**Options**:

* `-s, --state TEXT`: Filter by state (planned, started, paused, completed, canceled)
* `-t, --team TEXT`: Filter by team key (e.g., ENG, DESIGN)
* `--per-page INTEGER`: Number of projects per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived projects
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated  [default: updated]
* `--help`: Show this message and exit.

### `linear p view`

Get details of a specific Linear project.

Examples:

  # View project by ID
  linear projects view abc123-def456

   # View project as JSON
   linear projects view my-project --format json

**Usage**:

```console
$ linear p view [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear p create`

Create a new Linear project.

Examples:

  # Create a project with minimal fields
  linear projects create --name &quot;Q1 Initiative&quot; --team ENG

  # Create with multiple teams
  linear projects create --name &quot;Cross-team Project&quot; --team ENG --team DESIGN

  # Create with all fields
  linear projects create --name &quot;Q1 Initiative&quot; --team ENG           --description &quot;Focus area&quot; --state started           --target-date 2026-03-31 --lead user@example.com

**Usage**:

```console
$ linear p create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Project name (required)  [required]
* `-t, --team TEXT`: Team ID or key (can be used multiple times, required)  [required]
* `-d, --description TEXT`: Project description
* `-l, --lead TEXT`: Project lead (user email or ID)
* `--state TEXT`: Project state (planned, started, paused, completed, canceled)
* `--start-date TEXT`: Start date (YYYY-MM-DD)
* `--target-date TEXT`: Target date (YYYY-MM-DD)
* `--color TEXT`: Hex color code
* `--icon TEXT`: Icon name
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear p update`

Update an existing Linear project.

Examples:

  # Update project name
  linear projects update my-project --name &quot;New Name&quot;

  # Update multiple fields
  linear projects update my-project --name &quot;New Name&quot; --state completed

  # Update teams (replaces all teams)
  linear projects update my-project --team ENG --team PLATFORM

**Usage**:

```console
$ linear p update [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-n, --name TEXT`: New project name
* `-d, --description TEXT`: New project description
* `-t, --team TEXT`: Team ID or key (can be used multiple times, replaces all teams)
* `-l, --lead TEXT`: New project lead (user email or ID)
* `--state TEXT`: New project state (planned, started, paused, completed, canceled)
* `--start-date TEXT`: New start date (YYYY-MM-DD)
* `--target-date TEXT`: New target date (YYYY-MM-DD)
* `--color TEXT`: New hex color code
* `--icon TEXT`: New icon name
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear p delete`

Delete a Linear project.

Examples:

  # Delete project (with confirmation)
  linear projects delete my-project

  # Delete without confirmation
  linear projects delete my-project --yes

**Usage**:

```console
$ linear p delete [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear p archive`

Archive a Linear project.

Examples:

  # Archive project (with confirmation)
  linear projects archive my-project

  # Archive without confirmation
  linear projects archive my-project --yes

**Usage**:

```console
$ linear p archive [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear p unarchive`

Unarchive a Linear project.

Examples:

  # Unarchive project (with confirmation)
  linear projects unarchive my-project

  # Unarchive without confirmation
  linear projects unarchive my-project --yes

**Usage**:

```console
$ linear p unarchive [OPTIONS] PROJECT_ID
```

**Arguments**:

* `PROJECT_ID`: Project ID or slug  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear teams`

Manage Linear teams

**Usage**:

```console
$ linear teams [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear teams.
* `view`: Get details of a specific Linear team.
* `create`: Create a new Linear team.
* `update`: Update an existing Linear team.
* `delete`: Delete a Linear team.
* `archive`: Archive a Linear team.

### `linear teams list`

List Linear teams.

Examples:

  # List all teams
  linear teams list

  # Include archived teams
  linear teams list --include-archived

  # Fetch all results
  linear teams list --all

  # Pagination
  linear teams list --page 2 --per-page 10

  # Output as JSON
  linear teams list --format json

**Usage**:

```console
$ linear teams list [OPTIONS]
```

**Options**:

* `--per-page INTEGER`: Number of teams per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived teams
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear teams view`

Get details of a specific Linear team.

Examples:

  # View team by key
  linear teams view ENG

   # View team as JSON
   linear teams view ENG --format json

**Usage**:

```console
$ linear teams view [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear teams create`

Create a new Linear team.

Examples:

  # Create a new team
  linear teams create --name &quot;Engineering&quot; --key ENG

  # Create a private team with description
  linear teams create --name &quot;Design&quot; --key DESIGN --description &quot;Product design team&quot; --private

**Usage**:

```console
$ linear teams create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Team name (required)  [required]
* `-k, --key TEXT`: Team key (required)  [required]
* `-d, --description TEXT`: Team description
* `--private`: Make team private
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear teams update`

Update an existing Linear team.

Examples:

  # Update team name
  linear teams update ENG --name &quot;Engineering Team&quot;

  # Update multiple fields
  linear teams update ENG --name &quot;Core Engineering&quot; --description &quot;Backend team&quot;

  # Make team private
  linear teams update ENG --private

**Usage**:

```console
$ linear teams update [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-n, --name TEXT`: New team name
* `-k, --key TEXT`: New team key
* `-d, --description TEXT`: New team description
* `--private / --public`: Change team privacy
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear teams delete`

Delete a Linear team.

Examples:

  # Delete team (with confirmation)
  linear teams delete ENG

  # Delete without confirmation
  linear teams delete ENG --yes

**Usage**:

```console
$ linear teams delete [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear teams archive`

Archive a Linear team.

Examples:

  # Archive team (with confirmation)
  linear teams archive ENG

  # Archive without confirmation
  linear teams archive ENG --yes

**Usage**:

```console
$ linear teams archive [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear t`

Manage Linear teams

**Usage**:

```console
$ linear t [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear teams.
* `view`: Get details of a specific Linear team.
* `create`: Create a new Linear team.
* `update`: Update an existing Linear team.
* `delete`: Delete a Linear team.
* `archive`: Archive a Linear team.

### `linear t list`

List Linear teams.

Examples:

  # List all teams
  linear teams list

  # Include archived teams
  linear teams list --include-archived

  # Fetch all results
  linear teams list --all

  # Pagination
  linear teams list --page 2 --per-page 10

  # Output as JSON
  linear teams list --format json

**Usage**:

```console
$ linear t list [OPTIONS]
```

**Options**:

* `--per-page INTEGER`: Number of teams per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived teams
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear t view`

Get details of a specific Linear team.

Examples:

  # View team by key
  linear teams view ENG

   # View team as JSON
   linear teams view ENG --format json

**Usage**:

```console
$ linear t view [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear t create`

Create a new Linear team.

Examples:

  # Create a new team
  linear teams create --name &quot;Engineering&quot; --key ENG

  # Create a private team with description
  linear teams create --name &quot;Design&quot; --key DESIGN --description &quot;Product design team&quot; --private

**Usage**:

```console
$ linear t create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Team name (required)  [required]
* `-k, --key TEXT`: Team key (required)  [required]
* `-d, --description TEXT`: Team description
* `--private`: Make team private
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear t update`

Update an existing Linear team.

Examples:

  # Update team name
  linear teams update ENG --name &quot;Engineering Team&quot;

  # Update multiple fields
  linear teams update ENG --name &quot;Core Engineering&quot; --description &quot;Backend team&quot;

  # Make team private
  linear teams update ENG --private

**Usage**:

```console
$ linear t update [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-n, --name TEXT`: New team name
* `-k, --key TEXT`: New team key
* `-d, --description TEXT`: New team description
* `--private / --public`: Change team privacy
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear t delete`

Delete a Linear team.

Examples:

  # Delete team (with confirmation)
  linear teams delete ENG

  # Delete without confirmation
  linear teams delete ENG --yes

**Usage**:

```console
$ linear t delete [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear t archive`

Archive a Linear team.

Examples:

  # Archive team (with confirmation)
  linear teams archive ENG

  # Archive without confirmation
  linear teams archive ENG --yes

**Usage**:

```console
$ linear t archive [OPTIONS] TEAM_ID
```

**Arguments**:

* `TEAM_ID`: Team ID or key (e.g., &#x27;ENG&#x27;)  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear cycles`

Manage Linear cycles

**Usage**:

```console
$ linear cycles [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear cycles with optional filters.
* `view`: Get details of a specific Linear cycle.
* `create`: Create a new Linear cycle.
* `update`: Update an existing Linear cycle.
* `delete`: Delete a Linear cycle.
* `archive`: Archive a Linear cycle.

### `linear cycles list`

List Linear cycles with optional filters.

Examples:

  # List all cycles
  linear cycles list

  # Filter by team
  linear cycles list --team ENG

  # Show only active cycles
  linear cycles list --active

  # Show future cycles for a specific team
  linear cycles list --team design --future

  # Fetch all results
  linear cycles list --all

  # Pagination
  linear cycles list --page 2 --per-page 25

  # Output as JSON
  linear cycles list --format json

**Usage**:

```console
$ linear cycles list [OPTIONS]
```

**Options**:

* `-t, --team TEXT`: Filter by team name or key
* `-a, --active`: Show only active cycles
* `--future`: Show only future cycles
* `--past`: Show only past cycles
* `--per-page INTEGER`: Number of cycles per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `-l, --limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived cycles
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear cycles view`

Get details of a specific Linear cycle.

Examples:

  # View cycle by ID
  linear cycles view abc123-def456

   # View cycle as JSON
   linear cycles view abc123 --format json

**Usage**:

```console
$ linear cycles view [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear cycles create`

Create a new Linear cycle.

Examples:

  # Create a new cycle
  linear cycles create --name &quot;Sprint 1&quot; --team ENG --starts-at 2024-01-01 --ends-at 2024-01-14

  # With description
  linear cycles create --name &quot;Q1 Sprint 1&quot; --team ENG --starts-at 2024-01-01 --ends-at 2024-01-14 --description &quot;Focus on auth features&quot;

**Usage**:

```console
$ linear cycles create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Cycle name (required)  [required]
* `-t, --team TEXT`: Team ID or key (required)  [required]
* `--starts-at TEXT`: Start date (YYYY-MM-DD)  [required]
* `--ends-at TEXT`: End date (YYYY-MM-DD)  [required]
* `-d, --description TEXT`: Cycle description
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear cycles update`

Update an existing Linear cycle.

Examples:

  # Update cycle name
  linear cycles update abc123 --name &quot;Sprint 2&quot;

  # Update dates
  linear cycles update abc123 --starts-at 2024-01-15 --ends-at 2024-01-29

  # Update multiple fields
  linear cycles update abc123 --name &quot;Q1 Sprint 2&quot; --description &quot;Focus on dashboard&quot;

**Usage**:

```console
$ linear cycles update [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-n, --name TEXT`: New cycle name
* `--starts-at TEXT`: New start date (YYYY-MM-DD)
* `--ends-at TEXT`: New end date (YYYY-MM-DD)
* `-d, --description TEXT`: New cycle description
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear cycles delete`

Delete a Linear cycle.

Examples:

  # Delete cycle (with confirmation)
  linear cycles delete abc123

  # Delete without confirmation
  linear cycles delete abc123 --yes

**Usage**:

```console
$ linear cycles delete [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear cycles archive`

Archive a Linear cycle.

Examples:

  # Archive cycle (with confirmation)
  linear cycles archive abc123

  # Archive without confirmation
  linear cycles archive abc123 --yes

**Usage**:

```console
$ linear cycles archive [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear c`

Manage Linear cycles

**Usage**:

```console
$ linear c [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear cycles with optional filters.
* `view`: Get details of a specific Linear cycle.
* `create`: Create a new Linear cycle.
* `update`: Update an existing Linear cycle.
* `delete`: Delete a Linear cycle.
* `archive`: Archive a Linear cycle.

### `linear c list`

List Linear cycles with optional filters.

Examples:

  # List all cycles
  linear cycles list

  # Filter by team
  linear cycles list --team ENG

  # Show only active cycles
  linear cycles list --active

  # Show future cycles for a specific team
  linear cycles list --team design --future

  # Fetch all results
  linear cycles list --all

  # Pagination
  linear cycles list --page 2 --per-page 25

  # Output as JSON
  linear cycles list --format json

**Usage**:

```console
$ linear c list [OPTIONS]
```

**Options**:

* `-t, --team TEXT`: Filter by team name or key
* `-a, --active`: Show only active cycles
* `--future`: Show only future cycles
* `--past`: Show only past cycles
* `--per-page INTEGER`: Number of cycles per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `-l, --limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-archived`: Include archived cycles
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear c view`

Get details of a specific Linear cycle.

Examples:

  # View cycle by ID
  linear cycles view abc123-def456

   # View cycle as JSON
   linear cycles view abc123 --format json

**Usage**:

```console
$ linear c view [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear c create`

Create a new Linear cycle.

Examples:

  # Create a new cycle
  linear cycles create --name &quot;Sprint 1&quot; --team ENG --starts-at 2024-01-01 --ends-at 2024-01-14

  # With description
  linear cycles create --name &quot;Q1 Sprint 1&quot; --team ENG --starts-at 2024-01-01 --ends-at 2024-01-14 --description &quot;Focus on auth features&quot;

**Usage**:

```console
$ linear c create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Cycle name (required)  [required]
* `-t, --team TEXT`: Team ID or key (required)  [required]
* `--starts-at TEXT`: Start date (YYYY-MM-DD)  [required]
* `--ends-at TEXT`: End date (YYYY-MM-DD)  [required]
* `-d, --description TEXT`: Cycle description
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear c update`

Update an existing Linear cycle.

Examples:

  # Update cycle name
  linear cycles update abc123 --name &quot;Sprint 2&quot;

  # Update dates
  linear cycles update abc123 --starts-at 2024-01-15 --ends-at 2024-01-29

  # Update multiple fields
  linear cycles update abc123 --name &quot;Q1 Sprint 2&quot; --description &quot;Focus on dashboard&quot;

**Usage**:

```console
$ linear c update [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-n, --name TEXT`: New cycle name
* `--starts-at TEXT`: New start date (YYYY-MM-DD)
* `--ends-at TEXT`: New end date (YYYY-MM-DD)
* `-d, --description TEXT`: New cycle description
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear c delete`

Delete a Linear cycle.

Examples:

  # Delete cycle (with confirmation)
  linear cycles delete abc123

  # Delete without confirmation
  linear cycles delete abc123 --yes

**Usage**:

```console
$ linear c delete [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

### `linear c archive`

Archive a Linear cycle.

Examples:

  # Archive cycle (with confirmation)
  linear cycles archive abc123

  # Archive without confirmation
  linear cycles archive abc123 --yes

**Usage**:

```console
$ linear c archive [OPTIONS] CYCLE_ID
```

**Arguments**:

* `CYCLE_ID`: Cycle ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt
* `--help`: Show this message and exit.

## `linear users`

Manage Linear users

**Usage**:

```console
$ linear users [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear users in the workspace.
* `view`: Get details of a specific Linear user.

### `linear users list`

List Linear users in the workspace.

Examples:

  # List all active users
  linear users list

  # List all users including inactive
  linear users list --no-active-only

  # Fetch all results
  linear users list --all

  # Pagination
  linear users list --page 2 --per-page 10

  # Output as JSON
  linear users list --format json

**Usage**:

```console
$ linear users list [OPTIONS]
```

**Options**:

* `--active-only`: Show only active users  [default: True]
* `--per-page INTEGER`: Number of users per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `-l, --limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-disabled`: Include disabled users
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear users view`

Get details of a specific Linear user.

Examples:

  # View user by ID
  linear users view abc123-def456

  # View user by email
  linear users view user@example.com

   # View user as JSON
   linear users view abc123 --format json

**Usage**:

```console
$ linear users view [OPTIONS] USER_ID
```

**Arguments**:

* `USER_ID`: User ID or email  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

## `linear u`

Manage Linear users

**Usage**:

```console
$ linear u [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear users in the workspace.
* `view`: Get details of a specific Linear user.

### `linear u list`

List Linear users in the workspace.

Examples:

  # List all active users
  linear users list

  # List all users including inactive
  linear users list --no-active-only

  # Fetch all results
  linear users list --all

  # Pagination
  linear users list --page 2 --per-page 10

  # Output as JSON
  linear users list --format json

**Usage**:

```console
$ linear u list [OPTIONS]
```

**Options**:

* `--active-only`: Show only active users  [default: True]
* `--per-page INTEGER`: Number of users per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `-l, --limit INTEGER`: DEPRECATED: use --per-page instead
* `--include-disabled`: Include disabled users
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--help`: Show this message and exit.

### `linear u view`

Get details of a specific Linear user.

Examples:

  # View user by ID
  linear users view abc123-def456

  # View user by email
  linear users view user@example.com

   # View user as JSON
   linear users view abc123 --format json

**Usage**:

```console
$ linear u view [OPTIONS] USER_ID
```

**Arguments**:

* `USER_ID`: User ID or email  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

## `linear labels`

Manage Linear labels

**Usage**:

```console
$ linear labels [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List issue labels.
* `create`: Create a new label.
* `update`: Update an existing label.
* `delete`: Delete (permanently remove) a label.
* `archive`: Archive a label.

### `linear labels list`

List issue labels.

Examples:
    linear labels list
    linear labels list --team ENG
    linear labels list --per-page 20 --format json
    linear labels list --include-archived
    linear labels list --all
    linear labels list --page 2 --per-page 25

**Usage**:

```console
$ linear labels list [OPTIONS]
```

**Options**:

* `--per-page INTEGER`: Number of labels per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `-l, --limit INTEGER`: DEPRECATED: use --per-page instead
* `-t, --team TEXT`: Filter by team ID or key (e.g., &#x27;ENG&#x27;, &#x27;DESIGN&#x27;)
* `--include-archived`: Include archived labels
* `-f, --format TEXT`: Output format: table (default) or json  [default: table]
* `--help`: Show this message and exit.

### `linear labels create`

Create a new label.

Examples:
    linear labels create --name bug --color &quot;#FF0000&quot; --team ENG
    linear labels create --name feature --description &quot;New features&quot; --color blue
    linear labels create --name urgent  # Workspace-wide label

**Usage**:

```console
$ linear labels create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Label name (required)  [required]
* `-d, --description TEXT`: Label description
* `-c, --color TEXT`: Label color (hex like &quot;#FF0000&quot; or color name)
* `-t, --team TEXT`: Team ID or key (omit for workspace-wide label)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear labels update`

Update an existing label.

Examples:
    linear labels update &lt;label-id&gt; --name &quot;critical-bug&quot;
    linear labels update &lt;label-id&gt; --color &quot;#FF0000&quot; --description &quot;High priority bugs&quot;

**Usage**:

```console
$ linear labels update [OPTIONS] LABEL_ID
```

**Arguments**:

* `LABEL_ID`: Label ID  [required]

**Options**:

* `-n, --name TEXT`: New label name
* `-d, --description TEXT`: New label description
* `-c, --color TEXT`: New label color (hex like &quot;#FF0000&quot; or color name)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear labels delete`

Delete (permanently remove) a label.

Examples:
    linear labels delete &lt;label-id&gt;
    linear labels delete &lt;label-id&gt; --yes  # Skip confirmation

**Usage**:

```console
$ linear labels delete [OPTIONS] LABEL_ID
```

**Arguments**:

* `LABEL_ID`: Label ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt (permanently deletes the label)
* `--help`: Show this message and exit.

### `linear labels archive`

Archive a label.

Examples:
    linear labels archive &lt;label-id&gt;

**Usage**:

```console
$ linear labels archive [OPTIONS] LABEL_ID
```

**Arguments**:

* `LABEL_ID`: Label ID  [required]

**Options**:

* `--help`: Show this message and exit.

## `linear l`

Manage Linear labels

**Usage**:

```console
$ linear l [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List issue labels.
* `create`: Create a new label.
* `update`: Update an existing label.
* `delete`: Delete (permanently remove) a label.
* `archive`: Archive a label.

### `linear l list`

List issue labels.

Examples:
    linear labels list
    linear labels list --team ENG
    linear labels list --per-page 20 --format json
    linear labels list --include-archived
    linear labels list --all
    linear labels list --page 2 --per-page 25

**Usage**:

```console
$ linear l list [OPTIONS]
```

**Options**:

* `--per-page INTEGER`: Number of labels per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `-l, --limit INTEGER`: DEPRECATED: use --per-page instead
* `-t, --team TEXT`: Filter by team ID or key (e.g., &#x27;ENG&#x27;, &#x27;DESIGN&#x27;)
* `--include-archived`: Include archived labels
* `-f, --format TEXT`: Output format: table (default) or json  [default: table]
* `--help`: Show this message and exit.

### `linear l create`

Create a new label.

Examples:
    linear labels create --name bug --color &quot;#FF0000&quot; --team ENG
    linear labels create --name feature --description &quot;New features&quot; --color blue
    linear labels create --name urgent  # Workspace-wide label

**Usage**:

```console
$ linear l create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Label name (required)  [required]
* `-d, --description TEXT`: Label description
* `-c, --color TEXT`: Label color (hex like &quot;#FF0000&quot; or color name)
* `-t, --team TEXT`: Team ID or key (omit for workspace-wide label)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear l update`

Update an existing label.

Examples:
    linear labels update &lt;label-id&gt; --name &quot;critical-bug&quot;
    linear labels update &lt;label-id&gt; --color &quot;#FF0000&quot; --description &quot;High priority bugs&quot;

**Usage**:

```console
$ linear l update [OPTIONS] LABEL_ID
```

**Arguments**:

* `LABEL_ID`: Label ID  [required]

**Options**:

* `-n, --name TEXT`: New label name
* `-d, --description TEXT`: New label description
* `-c, --color TEXT`: New label color (hex like &quot;#FF0000&quot; or color name)
* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear l delete`

Delete (permanently remove) a label.

Examples:
    linear labels delete &lt;label-id&gt;
    linear labels delete &lt;label-id&gt; --yes  # Skip confirmation

**Usage**:

```console
$ linear l delete [OPTIONS] LABEL_ID
```

**Arguments**:

* `LABEL_ID`: Label ID  [required]

**Options**:

* `-y, --yes`: Skip confirmation prompt (permanently deletes the label)
* `--help`: Show this message and exit.

### `linear l archive`

Archive a label.

Examples:
    linear labels archive &lt;label-id&gt;

**Usage**:

```console
$ linear l archive [OPTIONS] LABEL_ID
```

**Arguments**:

* `LABEL_ID`: Label ID  [required]

**Options**:

* `--help`: Show this message and exit.

## `linear roadmaps`

Manage Linear roadmaps

**Usage**:

```console
$ linear roadmaps [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear roadmaps.
* `view`: Get details of a specific Linear roadmap.
* `create`: Create a new Linear roadmap.
* `update`: Update an existing Linear roadmap.

### `linear roadmaps list`

List Linear roadmaps.

Examples:

  # List all roadmaps
  linear roadmaps list

  # Fetch all results
  linear roadmaps list --all

  # Pagination
  linear roadmaps list --page 2 --per-page 25

  # Output as JSON
  linear roadmaps list --format json

**Usage**:

```console
$ linear roadmaps list [OPTIONS]
```

**Options**:

* `--per-page INTEGER`: Number of roadmaps per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--include-archived`: Include archived roadmaps
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated  [default: updated]
* `--help`: Show this message and exit.

### `linear roadmaps view`

Get details of a specific Linear roadmap.

Examples:

  # View roadmap by ID
  linear roadmaps view abc123-def456

   # View roadmap as JSON
   linear roadmaps view my-roadmap --format json

**Usage**:

```console
$ linear roadmaps view [OPTIONS] ROADMAP_ID
```

**Arguments**:

* `ROADMAP_ID`: Roadmap ID or slug  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear roadmaps create`

Create a new Linear roadmap.

Examples:

  # Create roadmap with name
  linear roadmaps create --name &quot;Q1 2024 Roadmap&quot;

  # Create roadmap with description
  linear roadmaps create --name &quot;Q1 2024&quot; --description &quot;Focus on core features&quot;

  # Create roadmap with editor for description
  linear roadmaps create --name &quot;Q1 2024&quot; --editor

  # Create roadmap with owner
  linear roadmaps create --name &quot;Q1 2024&quot; --owner-id user-123

**Usage**:

```console
$ linear roadmaps create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Roadmap name
* `-d, --description TEXT`: Roadmap description
* `--owner-id TEXT`: Owner user ID
* `-e, --editor`: Open editor for description
* `--help`: Show this message and exit.

### `linear roadmaps update`

Update an existing Linear roadmap.

Examples:

  # Update roadmap name
  linear roadmaps update abc123 --name &quot;Q2 2024 Roadmap&quot;

  # Update description
  linear roadmaps update abc123 --description &quot;Updated focus areas&quot;

  # Update with editor
  linear roadmaps update abc123 --editor

  # Update owner
  linear roadmaps update abc123 --owner-id user-456

**Usage**:

```console
$ linear roadmaps update [OPTIONS] ROADMAP_ID
```

**Arguments**:

* `ROADMAP_ID`: Roadmap ID or slug  [required]

**Options**:

* `-n, --name TEXT`: New roadmap name
* `-d, --description TEXT`: New description
* `--owner-id TEXT`: New owner user ID
* `-e, --editor`: Open editor for description
* `--help`: Show this message and exit.

## `linear r`

Manage Linear roadmaps

**Usage**:

```console
$ linear r [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List Linear roadmaps.
* `view`: Get details of a specific Linear roadmap.
* `create`: Create a new Linear roadmap.
* `update`: Update an existing Linear roadmap.

### `linear r list`

List Linear roadmaps.

Examples:

  # List all roadmaps
  linear roadmaps list

  # Fetch all results
  linear roadmaps list --all

  # Pagination
  linear roadmaps list --page 2 --per-page 25

  # Output as JSON
  linear roadmaps list --format json

**Usage**:

```console
$ linear r list [OPTIONS]
```

**Options**:

* `--per-page INTEGER`: Number of roadmaps per page (max 250)  [default: 50]
* `--page INTEGER`: Page number to fetch (starts at 1)
* `--all`: Fetch all results automatically
* `--include-archived`: Include archived roadmaps
* `-f, --format TEXT`: Output format: table, json  [default: table]
* `--order-by TEXT`: Sort by: created, updated  [default: updated]
* `--help`: Show this message and exit.

### `linear r view`

Get details of a specific Linear roadmap.

Examples:

  # View roadmap by ID
  linear roadmaps view abc123-def456

   # View roadmap as JSON
   linear roadmaps view my-roadmap --format json

**Usage**:

```console
$ linear r view [OPTIONS] ROADMAP_ID
```

**Arguments**:

* `ROADMAP_ID`: Roadmap ID or slug  [required]

**Options**:

* `-f, --format TEXT`: Output format: detail, json  [default: detail]
* `--help`: Show this message and exit.

### `linear r create`

Create a new Linear roadmap.

Examples:

  # Create roadmap with name
  linear roadmaps create --name &quot;Q1 2024 Roadmap&quot;

  # Create roadmap with description
  linear roadmaps create --name &quot;Q1 2024&quot; --description &quot;Focus on core features&quot;

  # Create roadmap with editor for description
  linear roadmaps create --name &quot;Q1 2024&quot; --editor

  # Create roadmap with owner
  linear roadmaps create --name &quot;Q1 2024&quot; --owner-id user-123

**Usage**:

```console
$ linear r create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Roadmap name
* `-d, --description TEXT`: Roadmap description
* `--owner-id TEXT`: Owner user ID
* `-e, --editor`: Open editor for description
* `--help`: Show this message and exit.

### `linear r update`

Update an existing Linear roadmap.

Examples:

  # Update roadmap name
  linear roadmaps update abc123 --name &quot;Q2 2024 Roadmap&quot;

  # Update description
  linear roadmaps update abc123 --description &quot;Updated focus areas&quot;

  # Update with editor
  linear roadmaps update abc123 --editor

  # Update owner
  linear roadmaps update abc123 --owner-id user-456

**Usage**:

```console
$ linear r update [OPTIONS] ROADMAP_ID
```

**Arguments**:

* `ROADMAP_ID`: Roadmap ID or slug  [required]

**Options**:

* `-n, --name TEXT`: New roadmap name
* `-d, --description TEXT`: New description
* `--owner-id TEXT`: New owner user ID
* `-e, --editor`: Open editor for description
* `--help`: Show this message and exit.
