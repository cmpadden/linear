"""Teams commands for Linear CLI."""

import sys

import typer
from typing_extensions import Annotated
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_team_detail,
    format_team_json,
    format_teams_json,
    format_teams_table,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear teams")


@app.command("list")
def list_teams(
    ctx: typer.Context,
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
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch teams
        teams = client.list_teams(
            limit=limit,
            include_archived=include_archived,
        )

        # Parse response

        # Format output
        if format == "json":
            format_teams_json(teams)
        else:  # table
            format_teams_table(teams)

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
def view_team(
    ctx: typer.Context,
    team_id: Annotated[str, typer.Argument(help="Team ID or key (e.g., 'ENG')")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear team.

    Examples:

      # View team by key
      linear teams view ENG

       # View team as JSON
       linear teams view ENG --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch team
        team = client.get_team(team_id)

        # Format output
        if format == "json":
            format_team_json(team)
        else:  # detail
            format_team_detail(team)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
