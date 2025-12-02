"""Linear CLI - Command line interface for Linear."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_compact,
    format_json,
    format_projects_compact,
    format_projects_json,
    format_projects_table,
    format_table,
)
from linear.models import parse_issues_response, parse_projects_response

app = typer.Typer(help="Linear CLI - Interact with Linear from your terminal")
issues_app = typer.Typer(help="Manage Linear issues")
projects_app = typer.Typer(help="Manage Linear projects")
app.add_typer(issues_app, name="issues")
app.add_typer(projects_app, name="projects")


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
    team: Annotated[Optional[str], typer.Option("--team", "-t", help="Filter by team name")] = None,
    priority: Annotated[
        Optional[int], typer.Option("--priority", help="Filter by priority (0-4)")
    ] = None,
    label: Annotated[
        Optional[list[str]], typer.Option("--label", "-l", help="Filter by label (repeatable)")
    ] = None,
    limit: Annotated[int, typer.Option("--limit", help="Number of issues to display")] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived issues")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json, compact")
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
        elif format == "compact":
            format_compact(issues)
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
        typer.Option("--state", "-s", help="Filter by state (planned, started, paused, completed, canceled)"),
    ] = None,
    team: Annotated[Optional[str], typer.Option("--team", "-t", help="Filter by team name")] = None,
    limit: Annotated[int, typer.Option("--limit", help="Number of projects to display")] = 50,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived projects")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json, compact")
    ] = "table",
    sort: Annotated[str, typer.Option("--sort", help="Sort by: created, updated")] = "updated",
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
        elif format == "compact":
            format_projects_compact(projects)
        else:  # table
            format_projects_table(projects)

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
