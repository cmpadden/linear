"""Cycles commands for Linear CLI."""

import sys
from typing import Optional, cast

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
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear cycles", no_args_is_help=True)


@app.command("list")
def list_cycles(
    ctx: typer.Context,
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
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of cycles per page (max 250)")
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

      # Fetch all results
      linear cycles list --all

      # Pagination
      linear cycles list --page 2 --per-page 25

      # Output as JSON
      linear cycles list --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        from rich.console import Console

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
        effective_per_page = limit if limit is not None else per_page
        if page and page > 1:
            # For now, we need to iterate through pages to get the cursor
            current_page = 1
            while current_page < page:
                _, page_info = client.list_cycles(
                    team=team,
                    active=active,
                    future=future,
                    past=past,
                    limit=effective_per_page,
                    include_archived=include_archived,
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

        # Fetch cycles
        cycles, pagination_info = client.list_cycles(
            team=team,
            active=active,
            future=future,
            past=past,
            limit=effective_per_page,
            include_archived=include_archived,
            after=after_cursor,
            fetch_all=all,
        )

        # Enhance pagination info for display
        display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
        if not all:
            start_index = ((page or 1) - 1) * effective_per_page + 1
            end_index = start_index + len(cycles) - 1
            display_pagination_info["startIndex"] = start_index
            display_pagination_info["endIndex"] = end_index
            display_pagination_info["currentPage"] = page or 1
            display_pagination_info["perPage"] = effective_per_page

        # Format output
        if format == "json":
            format_cycles_json(cycles)
        else:  # table
            format_cycles_table(cycles, display_pagination_info)

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
    ctx: typer.Context,
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
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

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


@app.command("create")
def create_cycle(
    ctx: typer.Context,
    name: Annotated[str, typer.Option("--name", "-n", help="Cycle name (required)")],
    team: Annotated[
        str, typer.Option("--team", "-t", help="Team ID or key (required)")
    ],
    starts_at: Annotated[
        str, typer.Option("--starts-at", help="Start date (YYYY-MM-DD)")
    ],
    ends_at: Annotated[str, typer.Option("--ends-at", help="End date (YYYY-MM-DD)")],
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Cycle description")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Create a new Linear cycle.

    Examples:

      # Create a new cycle
      linear cycles create --name "Sprint 1" --team ENG --starts-at 2024-01-01 --ends-at 2024-01-14

      # With description
      linear cycles create --name "Q1 Sprint 1" --team ENG --starts-at 2024-01-01 --ends-at 2024-01-14 --description "Focus on auth features"
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Resolve team ID
        try:
            team_obj = client.get_team(team)
            if not team_obj.id:
                console.print(f"[red]Error: Team '{team}' has no ID[/red]")
                sys.exit(1)
            team_id = cast(str, team_obj.id)
        except LinearClientError:
            console.print(f"[red]Error: Team '{team}' not found[/red]")
            sys.exit(1)

        # Create cycle
        cycle = client.create_cycle(
            name=name,
            team_id=team_id,
            starts_at=starts_at,
            ends_at=ends_at,
            description=description,
        )

        # Format output
        if format == "json":
            format_cycle_json(cycle)
        else:  # detail
            console.print(f"[green]✓[/green] Created cycle: {cycle.name}")
            format_cycle_detail(cycle)

    except LinearClientError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("update")
def update_cycle(
    ctx: typer.Context,
    cycle_id: Annotated[str, typer.Argument(help="Cycle ID")],
    name: Annotated[
        Optional[str], typer.Option("--name", "-n", help="New cycle name")
    ] = None,
    starts_at: Annotated[
        Optional[str], typer.Option("--starts-at", help="New start date (YYYY-MM-DD)")
    ] = None,
    ends_at: Annotated[
        Optional[str], typer.Option("--ends-at", help="New end date (YYYY-MM-DD)")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="New cycle description")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Update an existing Linear cycle.

    Examples:

      # Update cycle name
      linear cycles update abc123 --name "Sprint 2"

      # Update dates
      linear cycles update abc123 --starts-at 2024-01-15 --ends-at 2024-01-29

      # Update multiple fields
      linear cycles update abc123 --name "Q1 Sprint 2" --description "Focus on dashboard"
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Update cycle
        cycle = client.update_cycle(
            cycle_id=cycle_id,
            name=name,
            starts_at=starts_at,
            ends_at=ends_at,
            description=description,
        )

        # Format output
        if format == "json":
            format_cycle_json(cycle)
        else:  # detail
            console.print(f"[green]✓[/green] Updated cycle: {cycle.name}")
            format_cycle_detail(cycle)

    except LinearClientError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("delete")
def delete_cycle(
    ctx: typer.Context,
    cycle_id: Annotated[str, typer.Argument(help="Cycle ID")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Delete a Linear cycle.

    Examples:

      # Delete cycle (with confirmation)
      linear cycles delete abc123

      # Delete without confirmation
      linear cycles delete abc123 --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get cycle details for confirmation
        cycle = client.get_cycle(cycle_id)

        # Confirmation prompt
        if not yes:
            console.print("[yellow]Warning: You are about to delete cycle:[/yellow]")
            console.print(f"  Name: {cycle.name}")
            console.print(f"  Team: {cycle.team.key}")
            console.print(
                f"  Dates: {cycle.format_starts_at()} to {cycle.format_ends_at()}"
            )

            confirm = typer.confirm("Are you sure you want to delete this cycle?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Delete cycle
        client.delete_cycle(cycle_id)
        console.print(f"[green]✓[/green] Deleted cycle: {cycle.name}")

    except LinearClientError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("archive")
def archive_cycle(
    ctx: typer.Context,
    cycle_id: Annotated[str, typer.Argument(help="Cycle ID")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Archive a Linear cycle.

    Examples:

      # Archive cycle (with confirmation)
      linear cycles archive abc123

      # Archive without confirmation
      linear cycles archive abc123 --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get cycle details for confirmation
        cycle = client.get_cycle(cycle_id)

        # Confirmation prompt
        if not yes:
            console.print("[yellow]Warning: You are about to archive cycle:[/yellow]")
            console.print(f"  Name: {cycle.name}")
            console.print(f"  Team: {cycle.team.key}")
            console.print(
                f"  Dates: {cycle.format_starts_at()} to {cycle.format_ends_at()}"
            )

            confirm = typer.confirm("Are you sure you want to archive this cycle?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Archive cycle
        client.archive_cycle(cycle_id)
        console.print(f"[green]✓[/green] Archived cycle: {cycle.name}")

    except LinearClientError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
