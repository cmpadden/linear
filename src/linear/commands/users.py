"""Users commands for Linear CLI."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated
from pydantic import ValidationError
from rich.console import Console

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_user_detail,
    format_user_json,
    format_users_json,
    format_users_table,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear users", no_args_is_help=True)


@app.command("list")
def list_users(
    ctx: typer.Context,
    active_only: Annotated[
        bool, typer.Option("--active-only", help="Show only active users")
    ] = True,
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of users per page (max 250)")
    ] = 50,
    page: Annotated[
        Optional[int], typer.Option("--page", help="Page number to fetch (starts at 1)")
    ] = None,
    all: Annotated[
        bool, typer.Option("--all", help="Fetch all results automatically")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-l", help="DEPRECATED: use --per-page instead"),
    ] = None,
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

      # Fetch all results
      linear users list --all

      # Pagination
      linear users list --page 2 --per-page 10

      # Output as JSON
      linear users list --format json
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
        effective_per_page = per_page if limit is None else limit
        if page and page > 1:
            current_page = 1
            while current_page < page:
                _, page_info = client.list_users(
                    active_only=active_only,
                    limit=effective_per_page,
                    include_disabled=include_disabled,
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

        # Fetch users
        users, pagination_info = client.list_users(
            active_only=active_only,
            limit=effective_per_page,
            include_disabled=include_disabled,
            after=after_cursor,
            fetch_all=all,
        )

        # Enhance pagination info for display
        display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
        if not all:
            start_index = ((page or 1) - 1) * effective_per_page + 1
            end_index = start_index + len(users) - 1
            display_pagination_info["startIndex"] = start_index
            display_pagination_info["endIndex"] = end_index
            display_pagination_info["currentPage"] = page or 1
            display_pagination_info["perPage"] = effective_per_page

        # Format output
        if format == "json":
            format_users_json(users)
        else:  # table
            format_users_table(users, display_pagination_info)

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
def view_user(
    ctx: typer.Context,
    user_id: Annotated[str, typer.Argument(help="User ID or email")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear user.

    Examples:

      # View user by ID
      linear users view abc123-def456

      # View user by email
      linear users view user@example.com

       # View user as JSON
       linear users view abc123 --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch user
        user = client.get_user(user_id)

        # Format output
        if format == "json":
            format_user_json(user)
        else:  # detail
            format_user_detail(user)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
