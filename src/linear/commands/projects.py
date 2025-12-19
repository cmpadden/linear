"""Projects commands for Linear CLI."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated
from pydantic import ValidationError
from rich.console import Console

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_project_detail,
    format_project_json,
    format_projects_json,
    format_projects_table,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear projects")


@app.command("list")
def list_projects(
    ctx: typer.Context,
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
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of projects per page (max 250)")
    ] = 50,
    page: Annotated[
        Optional[int], typer.Option("--page", help="Page number to fetch (starts at 1)")
    ] = None,
    all: Annotated[
        bool, typer.Option("--all", help="Fetch all results automatically")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", help="DEPRECATED: use --per-page instead"),
    ] = None,
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

      # Fetch all results
      linear projects list --all

      # Pagination
      linear projects list --page 2 --per-page 25

      # Output as JSON
      linear projects list --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Handle deprecated --limit flag
        if limit is not None:
            console.print(
                "[yellow]Warning: --limit is deprecated, use --per-page instead[/yellow]"
            )
            per_page = limit

        # Validate per_page
        if per_page > 250:
            console.print("[red]Error: --per-page cannot exceed 250[/red]")
            sys.exit(1)

        # Calculate cursor for pagination
        after_cursor: str | None = None
        effective_per_page = (
            per_page if limit is None else limit
        )  # Handle if limit is used
        if page and page > 1:
            # For now, we need to iterate through pages to get the cursor
            current_page = 1
            while current_page < page:
                _, page_info = client.list_projects(
                    state=state,
                    team=team,
                    limit=effective_per_page,
                    include_archived=include_archived,
                    sort=order_by,
                    after=after_cursor,
                    fetch_all=False,
                )
                cursor_value = page_info.get("endCursor")
                if not cursor_value or cursor_value == "":
                    console.print(
                        f"[yellow]Page {page} does not exist (only {current_page} page(s) available)[/yellow]"
                    )
                    sys.exit(1)
                after_cursor = str(cursor_value) if cursor_value else None
                current_page += 1

        # Fetch projects
        projects, pagination_info = client.list_projects(
            state=state,
            team=team,
            limit=effective_per_page,
            include_archived=include_archived,
            sort=order_by,
            after=after_cursor,
            fetch_all=all,
        )

        # Enhance pagination info for display
        display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
        if not all:
            start_index = ((page or 1) - 1) * effective_per_page + 1
            end_index = start_index + len(projects) - 1
            display_pagination_info["startIndex"] = start_index
            display_pagination_info["endIndex"] = end_index
            display_pagination_info["currentPage"] = page or 1
            display_pagination_info["perPage"] = effective_per_page

        # Format output
        if format == "json":
            format_projects_json(projects)
        else:  # table
            format_projects_table(projects, display_pagination_info)

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
    ctx: typer.Context,
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
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

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
