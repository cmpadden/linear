"""Projects commands for Linear CLI."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_project_detail,
    format_project_json,
    format_projects_json,
    format_projects_table,
)

app = typer.Typer(help="Manage Linear projects")


@app.command("list")
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
        Optional[str],
        typer.Option("--team", "-t", help="Filter by team key (e.g., ENG, DESIGN)"),
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
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort by: created, updated")
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
        projects = client.list_projects(
            state=state,
            team=team,
            limit=limit,
            include_archived=include_archived,
            sort=order_by,
        )

        # Parse response

        # Format output
        if format == "json":
            format_projects_json(projects)
        else:  # table
            format_projects_table(projects)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("view")
def view_project(
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear project.

    Examples:

      # View project by ID
      linear projects view abc123-def456

      # View project as JSON
      linear projects view my-project --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch project
        project = client.get_project(project_id)

        # Format output
        if format == "json":
            format_project_json(project)
        else:  # detail
            format_project_detail(project)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
