"""Linear CLI - Command line interface for Linear."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_cycle_detail,
    format_cycle_json,
    format_cycles_json,
    format_cycles_table,
    format_issue_detail,
    format_issue_json,
    format_json,
    format_project_detail,
    format_project_json,
    format_projects_json,
    format_projects_table,
    format_table,
    format_team_detail,
    format_team_json,
    format_teams_json,
    format_teams_table,
    format_user_detail,
    format_user_json,
    format_users_json,
    format_users_table,
)
from linear.models import (
    parse_cycles_response,
    parse_issues_response,
    parse_projects_response,
    parse_teams_response,
    parse_users_response,
)

app = typer.Typer(
    help="Linear CLI - Interact with Linear from your terminal", no_args_is_help=True
)
issues_app = typer.Typer(help="Manage Linear issues")
projects_app = typer.Typer(help="Manage Linear projects")
teams_app = typer.Typer(help="Manage Linear teams")
cycles_app = typer.Typer(help="Manage Linear cycles", no_args_is_help=True)
users_app = typer.Typer(help="Manage Linear users", no_args_is_help=True)
app.add_typer(issues_app, name="issues")
app.add_typer(projects_app, name="projects")
app.add_typer(teams_app, name="teams")
app.add_typer(cycles_app, name="cycles")
app.add_typer(users_app, name="users")


@issues_app.command("list")
def list_issues(
    assignee: Annotated[
        Optional[str], typer.Option("--assignee", "-a", help="Filter by assignee email")
    ] = None,
    project: Annotated[
        Optional[str], typer.Option("--project", "-p", help="Filter by project name")
    ] = None,
    status: Annotated[
        Optional[str], typer.Option("--status", "-s", help="Filter by status")
    ] = None,
    team: Annotated[
        Optional[str], typer.Option("--team", "-t", help="Filter by team name")
    ] = None,
    priority: Annotated[
        Optional[int], typer.Option("--priority", help="Filter by priority (0-4)")
    ] = None,
    label: Annotated[
        Optional[list[str]],
        typer.Option("--label", "-l", help="Filter by label (repeatable)"),
    ] = None,
    limit: Annotated[
        int, typer.Option("--limit", help="Number of issues to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived issues")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    sort: Annotated[
        str, typer.Option("--sort", help="Sort by: created, updated, priority")
    ] = "updated",
) -> None:
    """List Linear issues with optional filters.

    Examples:

      # List all issues
      linear issues list

      # Filter by assignee
      linear issues list --assignee user@example.com

      # Filter by multiple criteria
      linear issues list --status "in progress" --priority 1 --limit 10

      # Output as JSON
      linear issues list --format json

      # Filter by labels
      linear issues list --label bug --label urgent
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch issues
        response = client.list_issues(
            assignee=assignee,
            project=project,
            status=status,
            team=team,
            priority=priority,
            labels=label,
            limit=limit,
            include_archived=include_archived,
            sort=sort,
        )

        # Parse response
        issues = parse_issues_response(response)

        # Format output
        if format == "json":
            format_json(issues)
        else:  # table
            format_table(issues)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@issues_app.command("get")
def get_issue(
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear issue.

    Examples:

      # Get issue by identifier
      linear issues get ENG-123

      # Get issue as JSON
      linear issues get ENG-123 --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch issue
        response = client.get_issue(issue_id)

        # Format output
        if format == "json":
            format_issue_json(response)
        else:  # detail
            format_issue_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@issues_app.command("search")
def search_issues(
    query: Annotated[str, typer.Argument(help="Search query (searches issue titles)")],
    limit: Annotated[
        int, typer.Option("--limit", help="Number of issues to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived issues")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    sort: Annotated[
        str, typer.Option("--sort", help="Sort by: created, updated, priority")
    ] = "updated",
) -> None:
    """Search Linear issues by title.

    Examples:

      # Search for issues with "authentication" in title
      linear issues search authentication

      # Search with output as JSON
      linear issues search "bug fix" --format json

      # Limit results
      linear issues search refactor --limit 10
    """
    try:
        # Initialize client
        client = LinearClient()

        # Search issues
        response = client.search_issues(
            query=query,
            limit=limit,
            include_archived=include_archived,
            sort=sort,
        )

        # Parse response
        issues = parse_issues_response(response)

        # Format output
        if format == "json":
            format_json(issues)
        else:  # table
            format_table(issues)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@projects_app.command("list")
def list_projects(
    state: Annotated[
        Optional[str],
        typer.Option(
            "--state",
            "-s",
            help="Filter by state (planned, started, paused, completed, canceled)",
        ),
    ] = None,
    team: Annotated[
        Optional[str], typer.Option("--team", "-t", help="Filter by team name")
    ] = None,
    limit: Annotated[
        int, typer.Option("--limit", help="Number of projects to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived projects")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    sort: Annotated[
        str, typer.Option("--sort", help="Sort by: created, updated")
    ] = "updated",
) -> None:
    """List Linear projects with optional filters.

    Examples:

      # List all projects
      linear projects list

      # Filter by state
      linear projects list --state started

      # Filter by team
      linear projects list --team engineering

      # Output as JSON
      linear projects list --format json

      # Limit results
      linear projects list --limit 10
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch projects
        response = client.list_projects(
            state=state,
            team=team,
            limit=limit,
            include_archived=include_archived,
            sort=sort,
        )

        # Parse response
        projects = parse_projects_response(response)

        # Format output
        if format == "json":
            format_projects_json(projects)
        else:  # table
            format_projects_table(projects)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@projects_app.command("get")
def get_project(
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear project.

    Examples:

      # Get project by ID
      linear projects get abc123-def456

      # Get project as JSON
      linear projects get my-project --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch project
        response = client.get_project(project_id)

        # Format output
        if format == "json":
            format_project_json(response)
        else:  # detail
            format_project_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@teams_app.command("list")
def list_teams(
    limit: Annotated[
        int, typer.Option("--limit", help="Number of teams to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived teams")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List Linear teams.

    Examples:

      # List all teams
      linear teams list

      # Include archived teams
      linear teams list --include-archived

      # Output as JSON
      linear teams list --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch teams
        response = client.list_teams(
            limit=limit,
            include_archived=include_archived,
        )

        # Parse response
        teams = parse_teams_response(response)

        # Format output
        if format == "json":
            format_teams_json(teams)
        else:  # table
            format_teams_table(teams)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@teams_app.command("get")
def get_team(
    team_id: Annotated[str, typer.Argument(help="Team ID or key (e.g., 'ENG')")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear team.

    Examples:

      # Get team by key
      linear teams get ENG

      # Get team as JSON
      linear teams get ENG --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch team
        response = client.get_team(team_id)

        # Format output
        if format == "json":
            format_team_json(response)
        else:  # detail
            format_team_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cycles_app.command("list")
def list_cycles(
    team: Annotated[
        Optional[str], typer.Option("--team", "-t", help="Filter by team name or key")
    ] = None,
    active: Annotated[
        bool, typer.Option("--active", "-a", help="Show only active cycles")
    ] = False,
    future: Annotated[
        bool, typer.Option("--future", help="Show only future cycles")
    ] = False,
    past: Annotated[bool, typer.Option("--past", help="Show only past cycles")] = False,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Number of cycles to display")
    ] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived cycles")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List Linear cycles with optional filters.

    Examples:

      # List all cycles
      linear cycles list

      # Filter by team
      linear cycles list --team ENG

      # Show only active cycles
      linear cycles list --active

      # Show future cycles for a specific team
      linear cycles list --team design --future

      # Output as JSON
      linear cycles list --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch cycles
        response = client.list_cycles(
            team=team,
            active=active,
            future=future,
            past=past,
            limit=limit,
            include_archived=include_archived,
        )

        # Parse cycles
        cycles = parse_cycles_response(response)

        # Format output
        if format == "json":
            format_cycles_json(cycles)
        else:  # table
            format_cycles_table(cycles)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cycles_app.command("get")
def get_cycle(
    cycle_id: Annotated[str, typer.Argument(help="Cycle ID")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear cycle.

    Examples:

      # Get cycle by ID
      linear cycles get abc123-def456

      # Get cycle as JSON
      linear cycles get abc123 --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch cycle
        response = client.get_cycle(cycle_id)

        # Format output
        if format == "json":
            format_cycle_json(response)
        else:  # detail
            format_cycle_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@users_app.command("list")
def list_users(
    active_only: Annotated[
        bool, typer.Option("--active-only", help="Show only active users")
    ] = True,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Number of users to display")
    ] = 50,
    include_disabled: Annotated[
        bool, typer.Option("--include-disabled", help="Include disabled users")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List Linear users in the workspace.

    Examples:

      # List all active users
      linear users list

      # List all users including inactive
      linear users list --no-active-only

      # List with limit
      linear users list --limit 20

      # Output as JSON
      linear users list --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch users
        response = client.list_users(
            active_only=active_only,
            limit=limit,
            include_disabled=include_disabled,
        )

        # Parse users
        users = parse_users_response(response)

        # Format output
        if format == "json":
            format_users_json(users)
        else:  # table
            format_users_table(users)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@users_app.command("get")
def get_user(
    user_id: Annotated[str, typer.Argument(help="User ID or email")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear user.

    Examples:

      # Get user by ID
      linear users get abc123-def456

      # Get user by email
      linear users get user@example.com

      # Get user as JSON
      linear users get abc123 --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch user
        response = client.get_user(user_id)

        # Format output
        if format == "json":
            format_user_json(response)
        else:  # detail
            format_user_detail(response)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
