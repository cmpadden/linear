"""Cycles commands for Linear CLI."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_cycle_detail,
    format_cycle_json,
    format_cycles_json,
    format_cycles_table,
)

app = typer.Typer(help="Manage Linear cycles", no_args_is_help=True)


@app.command("list")
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
        cycles = client.list_cycles(
            team=team,
            active=active,
            future=future,
            past=past,
            limit=limit,
            include_archived=include_archived,
        )

        # Parse cycles

        # Format output
        if format == "json":
            format_cycles_json(cycles)
        else:  # table
            format_cycles_table(cycles)

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
def view_cycle(
    cycle_id: Annotated[str, typer.Argument(help="Cycle ID")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear cycle.

    Examples:

      # View cycle by ID
      linear cycles view abc123-def456

      # View cycle as JSON
      linear cycles view abc123 --format json
    """
    try:
        # Initialize client
        client = LinearClient()

        # Fetch cycle
        cycle = client.get_cycle(cycle_id)

        # Format output
        if format == "json":
            format_cycle_json(cycle)
        else:  # detail
            format_cycle_detail(cycle)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
