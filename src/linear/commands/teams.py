"""Teams commands for Linear CLI."""

import sys
from typing import Optional

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


@app.command("create")
def create_team(
    ctx: typer.Context,
    name: Annotated[str, typer.Option("--name", "-n", help="Team name (required)")],
    key: Annotated[str, typer.Option("--key", "-k", help="Team key (required)")],
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Team description")
    ] = None,
    private: Annotated[
        bool, typer.Option("--private", help="Make team private")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Create a new Linear team.

    Examples:

      # Create a new team
      linear teams create --name "Engineering" --key ENG

      # Create a private team with description
      linear teams create --name "Design" --key DESIGN --description "Product design team" --private
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Create team
        team = client.create_team(
            name=name,
            key=key,
            description=description,
            private=private,
        )

        # Format output
        if format == "json":
            format_team_json(team)
        else:  # detail
            console.print(f"[green]✓[/green] Created team: {team.name}")
            format_team_detail(team)

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
def update_team(
    ctx: typer.Context,
    team_id: Annotated[str, typer.Argument(help="Team ID or key (e.g., 'ENG')")],
    name: Annotated[
        Optional[str], typer.Option("--name", "-n", help="New team name")
    ] = None,
    key: Annotated[
        Optional[str], typer.Option("--key", "-k", help="New team key")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="New team description")
    ] = None,
    private: Annotated[
        Optional[bool], typer.Option("--private/--public", help="Change team privacy")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Update an existing Linear team.

    Examples:

      # Update team name
      linear teams update ENG --name "Engineering Team"

      # Update multiple fields
      linear teams update ENG --name "Core Engineering" --description "Backend team"

      # Make team private
      linear teams update ENG --private
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Update team
        team = client.update_team(
            team_id=team_id,
            name=name,
            key=key,
            description=description,
            private=private,
        )

        # Format output
        if format == "json":
            format_team_json(team)
        else:  # detail
            console.print(f"[green]✓[/green] Updated team: {team.name}")
            format_team_detail(team)

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
def delete_team(
    ctx: typer.Context,
    team_id: Annotated[str, typer.Argument(help="Team ID or key (e.g., 'ENG')")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Delete a Linear team.

    Examples:

      # Delete team (with confirmation)
      linear teams delete ENG

      # Delete without confirmation
      linear teams delete ENG --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get team details for confirmation
        team = client.get_team(team_id)

        # Confirmation prompt
        if not yes:
            console.print("[yellow]Warning: You are about to delete team:[/yellow]")
            console.print(f"  Name: {team.name}")
            console.print(f"  Key: {team.key}")
            if team.description:
                console.print(f"  Description: {team.description}")

            confirm = typer.confirm("Are you sure you want to delete this team?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Delete team
        client.delete_team(team_id)
        console.print(f"[green]✓[/green] Deleted team: {team.name}")

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
def archive_team(
    ctx: typer.Context,
    team_id: Annotated[str, typer.Argument(help="Team ID or key (e.g., 'ENG')")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Archive a Linear team.

    Examples:

      # Archive team (with confirmation)
      linear teams archive ENG

      # Archive without confirmation
      linear teams archive ENG --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        from rich.console import Console

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get team details for confirmation
        team = client.get_team(team_id)

        # Confirmation prompt
        if not yes:
            console.print("[yellow]Warning: You are about to archive team:[/yellow]")
            console.print(f"  Name: {team.name}")
            console.print(f"  Key: {team.key}")
            if team.description:
                console.print(f"  Description: {team.description}")

            confirm = typer.confirm("Are you sure you want to archive this team?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Archive team
        client.archive_team(team_id)
        console.print(f"[green]✓[/green] Archived team: {team.name}")

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
