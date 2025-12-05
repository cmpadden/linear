"""Users commands for Linear CLI."""

import sys

import typer
from typing_extensions import Annotated
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_user_detail,
    format_user_json,
    format_users_json,
    format_users_table,
)

app = typer.Typer(help="Manage Linear users", no_args_is_help=True)


@app.command("list")
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
        users = client.list_users(
            active_only=active_only,
            limit=limit,
            include_disabled=include_disabled,
        )

        # Parse users

        # Format output
        if format == "json":
            format_users_json(users)
        else:  # table
            format_users_table(users)

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
        # Initialize client
        client = LinearClient()

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
