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

app = typer.Typer(help="Manage Linear projects", no_args_is_help=True)


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


@app.command("create")
def create_project(
    ctx: typer.Context,
    name: Annotated[str, typer.Option("--name", "-n", help="Project name (required)")],
    team: Annotated[
        list[str],
        typer.Option(
            "--team", "-t", help="Team ID or key (can be used multiple times, required)"
        ),
    ],
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Project description")
    ] = None,
    lead: Annotated[
        Optional[str],
        typer.Option("--lead", "-l", help="Project lead (user email or ID)"),
    ] = None,
    state: Annotated[
        Optional[str],
        typer.Option(
            "--state",
            help="Project state (planned, started, paused, completed, canceled)",
        ),
    ] = None,
    start_date: Annotated[
        Optional[str],
        typer.Option("--start-date", help="Start date (YYYY-MM-DD)"),
    ] = None,
    target_date: Annotated[
        Optional[str],
        typer.Option("--target-date", help="Target date (YYYY-MM-DD)"),
    ] = None,
    color: Annotated[
        Optional[str], typer.Option("--color", help="Hex color code")
    ] = None,
    icon: Annotated[Optional[str], typer.Option("--icon", help="Icon name")] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Create a new Linear project.

    Examples:

      # Create a project with minimal fields
      linear projects create --name "Q1 Initiative" --team ENG

      # Create with multiple teams
      linear projects create --name "Cross-team Project" --team ENG --team DESIGN

      # Create with all fields
      linear projects create --name "Q1 Initiative" --team ENG \
          --description "Focus area" --state started \
          --target-date 2026-03-31 --lead user@example.com
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Validate state if provided
        if state:
            VALID_STATES = ["planned", "started", "paused", "completed", "canceled"]
            if state.lower() not in VALID_STATES:
                console.print(
                    f"[red]Error: Invalid state. Valid states: {', '.join(VALID_STATES)}[/red]"
                )
                sys.exit(1)

        # Resolve team IDs
        from typing import cast

        team_ids = []
        for team_identifier in team:
            try:
                team_obj = client.get_team(team_identifier)
                if not team_obj.id:
                    console.print(
                        f"[red]Error: Team '{team_identifier}' has no ID[/red]"
                    )
                    sys.exit(1)
                team_ids.append(cast(str, team_obj.id))
            except LinearClientError:
                console.print(f"[red]Error: Team '{team_identifier}' not found[/red]")
                sys.exit(1)

        # Resolve lead ID if provided
        lead_id = None
        if lead:
            try:
                user = client.get_user(lead)
                if not user.id:
                    console.print(f"[red]Error: User '{lead}' has no ID[/red]")
                    sys.exit(1)
                lead_id = cast(str, user.id)
            except LinearClientError:
                console.print(f"[red]Error: User '{lead}' not found[/red]")
                sys.exit(1)

        # Create project
        project = client.create_project(
            name=name,
            team_ids=team_ids,
            description=description,
            lead_id=lead_id,
            state=state,
            start_date=start_date,
            target_date=target_date,
            color=color,
            icon=icon,
        )

        # Format output
        console.print(f"[green]✓[/green] Created project: {project.name}")
        if format == "json":
            format_project_json(project)
        else:  # detail
            format_project_detail(project)

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("update")
def update_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    name: Annotated[
        Optional[str], typer.Option("--name", "-n", help="New project name")
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option("--description", "-d", help="New project description"),
    ] = None,
    team: Annotated[
        Optional[list[str]],
        typer.Option(
            "--team",
            "-t",
            help="Team ID or key (can be used multiple times, replaces all teams)",
        ),
    ] = None,
    lead: Annotated[
        Optional[str],
        typer.Option("--lead", "-l", help="New project lead (user email or ID)"),
    ] = None,
    state: Annotated[
        Optional[str],
        typer.Option(
            "--state",
            help="New project state (planned, started, paused, completed, canceled)",
        ),
    ] = None,
    start_date: Annotated[
        Optional[str],
        typer.Option("--start-date", help="New start date (YYYY-MM-DD)"),
    ] = None,
    target_date: Annotated[
        Optional[str],
        typer.Option("--target-date", help="New target date (YYYY-MM-DD)"),
    ] = None,
    color: Annotated[
        Optional[str], typer.Option("--color", help="New hex color code")
    ] = None,
    icon: Annotated[Optional[str], typer.Option("--icon", help="New icon name")] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Update an existing Linear project.

    Examples:

      # Update project name
      linear projects update my-project --name "New Name"

      # Update multiple fields
      linear projects update my-project --name "New Name" --state completed

      # Update teams (replaces all teams)
      linear projects update my-project --team ENG --team PLATFORM
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Validate that at least one field is provided
        if not any(
            [name, description, team, lead, state, start_date, target_date, color, icon]
        ):
            console.print(
                "[red]Error: At least one field to update must be provided[/red]"
            )
            sys.exit(1)

        # Validate state if provided
        if state:
            VALID_STATES = ["planned", "started", "paused", "completed", "canceled"]
            if state.lower() not in VALID_STATES:
                console.print(
                    f"[red]Error: Invalid state. Valid states: {', '.join(VALID_STATES)}[/red]"
                )
                sys.exit(1)

        # Resolve team IDs if provided
        from typing import cast

        team_ids = None
        if team:
            team_ids = []
            for team_identifier in team:
                try:
                    team_obj = client.get_team(team_identifier)
                    if not team_obj.id:
                        console.print(
                            f"[red]Error: Team '{team_identifier}' has no ID[/red]"
                        )
                        sys.exit(1)
                    team_ids.append(cast(str, team_obj.id))
                except LinearClientError:
                    console.print(
                        f"[red]Error: Team '{team_identifier}' not found[/red]"
                    )
                    sys.exit(1)

        # Resolve lead ID if provided
        lead_id = None
        if lead:
            try:
                user = client.get_user(lead)
                if not user.id:
                    console.print(f"[red]Error: User '{lead}' has no ID[/red]")
                    sys.exit(1)
                lead_id = cast(str, user.id)
            except LinearClientError:
                console.print(f"[red]Error: User '{lead}' not found[/red]")
                sys.exit(1)

        # Update project
        project = client.update_project(
            project_id=project_id,
            name=name,
            description=description,
            team_ids=team_ids,
            lead_id=lead_id,
            state=state,
            start_date=start_date,
            target_date=target_date,
            color=color,
            icon=icon,
        )

        # Format output
        console.print(f"[green]✓[/green] Updated project: {project.name}")
        if format == "json":
            format_project_json(project)
        else:  # detail
            format_project_detail(project)

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("delete")
def delete_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Delete a Linear project.

    Examples:

      # Delete project (with confirmation)
      linear projects delete my-project

      # Delete without confirmation
      linear projects delete my-project --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get project details for confirmation
        project = client.get_project(project_id)

        # Confirmation prompt
        if not yes:
            console.print("[yellow]Warning: You are about to delete project:[/yellow]")
            console.print(f"  Name: {project.name}")
            console.print(f"  State: {project.state}")
            if project.teams:
                team_names = ", ".join(t.name for t in project.teams)
                console.print(f"  Teams: {team_names}")
            console.print(f"  Lead: {project.format_lead()}")

            confirm = typer.confirm("Are you sure you want to delete this project?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Delete project
        client.delete_project(project_id)
        console.print(f"[green]✓[/green] Deleted project: {project.name}")

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("archive")
def archive_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Archive a Linear project.

    Examples:

      # Archive project (with confirmation)
      linear projects archive my-project

      # Archive without confirmation
      linear projects archive my-project --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get project details for confirmation
        project = client.get_project(project_id)

        # Confirmation prompt
        if not yes:
            console.print("[yellow]Warning: You are about to archive project:[/yellow]")
            console.print(f"  Name: {project.name}")
            console.print(f"  State: {project.state}")
            if project.teams:
                team_names = ", ".join(t.name for t in project.teams)
                console.print(f"  Teams: {team_names}")
            console.print(f"  Lead: {project.format_lead()}")

            confirm = typer.confirm("Are you sure you want to archive this project?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Archive project
        client.archive_project(project_id)
        console.print(f"[green]✓[/green] Archived project: {project.name}")

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("unarchive")
def unarchive_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID or slug")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
) -> None:
    """Unarchive a Linear project.

    Examples:

      # Unarchive project (with confirmation)
      linear projects unarchive my-project

      # Unarchive without confirmation
      linear projects unarchive my-project --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        console = Console()
        client = LinearClient(verbose_logger=verbose_logger)

        # Get project details for confirmation
        project = client.get_project(project_id)

        # Confirmation prompt
        if not yes:
            console.print(
                "[yellow]Warning: You are about to unarchive project:[/yellow]"
            )
            console.print(f"  Name: {project.name}")
            console.print(f"  State: {project.state}")
            if project.teams:
                team_names = ", ".join(t.name for t in project.teams)
                console.print(f"  Teams: {team_names}")
            console.print(f"  Lead: {project.format_lead()}")

            confirm = typer.confirm("Are you sure you want to unarchive this project?")
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                sys.exit(0)

        # Unarchive project
        client.unarchive_project(project_id)
        console.print(f"[green]✓[/green] Unarchived project: {project.name}")

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
