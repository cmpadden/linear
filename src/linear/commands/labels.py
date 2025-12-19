"""Labels commands for Linear CLI."""

import sys
from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_labels_json,
    format_labels_table,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear labels", no_args_is_help=True)


@app.command("list")
def list_labels(
    ctx: typer.Context,
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of labels per page (max 250)")
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
    team: Annotated[
        Optional[str],
        typer.Option(
            "--team", "-t", help="Filter by team ID or key (e.g., 'ENG', 'DESIGN')"
        ),
    ] = None,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived labels")
    ] = False,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: table (default) or json"),
    ] = "table",
) -> None:
    """List issue labels.

    Examples:
        linear labels list
        linear labels list --team ENG
        linear labels list --per-page 20 --format json
        linear labels list --include-archived
        linear labels list --all
        linear labels list --page 2 --per-page 25
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
        effective_per_page = per_page
        if page and page > 1:
            # For now, we need to iterate through pages to get the cursor
            current_page = 1
            while current_page < page:
                _, page_info = client.list_labels(
                    limit=effective_per_page,
                    team=team,
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

        # Fetch labels
        labels, pagination_info = client.list_labels(
            limit=effective_per_page,
            team=team,
            include_archived=include_archived,
            after=after_cursor,
            fetch_all=all,
        )

        # Enhance pagination info for display
        display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
        if not all:
            start_index = ((page or 1) - 1) * effective_per_page + 1
            end_index = start_index + len(labels) - 1
            display_pagination_info["startIndex"] = start_index
            display_pagination_info["endIndex"] = end_index
            display_pagination_info["currentPage"] = page or 1
            display_pagination_info["perPage"] = effective_per_page

        # Format output
        if format == "json":
            format_labels_json(labels)
        else:  # table
            format_labels_table(labels, display_pagination_info)

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
def create_label(
    ctx: typer.Context,
    name: Annotated[str, typer.Option("--name", "-n", help="Label name (required)")],
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Label description")
    ] = None,
    color: Annotated[
        Optional[str],
        typer.Option(
            "--color", "-c", help='Label color (hex like "#FF0000" or color name)'
        ),
    ] = None,
    team: Annotated[
        Optional[str],
        typer.Option(
            "--team", "-t", help="Team ID or key (omit for workspace-wide label)"
        ),
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Create a new label.

    Examples:
        linear labels create --name bug --color "#FF0000" --team ENG
        linear labels create --name feature --description "New features" --color blue
        linear labels create --name urgent  # Workspace-wide label
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Resolve team ID if team key/name provided
        team_id: str | None = None
        if team:
            # Check if it's already a UUID
            if "-" in team and len(team) == 36:
                team_id = team
            else:
                # Try to resolve by key or name
                teams, _ = client.list_teams(limit=100)
                team_id = None
                for t in teams:
                    if (t.key and t.key.upper() == team.upper()) or (
                        t.name and team.lower() in t.name.lower()
                    ):
                        team_id = t.id
                        break

                if team_id is None:
                    console.print(f"[red]Error: Team '{team}' not found[/red]")
                    sys.exit(1)

        # Create label
        label = client.create_label(
            name=name,
            team_id=team_id,
            description=description,
            color=color,
        )

        # Display success message
        console.print(f"[green]✓[/green] Created label: {label.name} ({label.id})")

        # Format output
        if format == "json":
            format_labels_json([label])
        else:  # detail
            format_labels_table([label])

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
def update_label(
    ctx: typer.Context,
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    name: Annotated[
        Optional[str], typer.Option("--name", "-n", help="New label name")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="New label description")
    ] = None,
    color: Annotated[
        Optional[str],
        typer.Option(
            "--color", "-c", help='New label color (hex like "#FF0000" or color name)'
        ),
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Update an existing label.

    Examples:
        linear labels update <label-id> --name "critical-bug"
        linear labels update <label-id> --color "#FF0000" --description "High priority bugs"
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Check that at least one field is being updated
        if not any([name, description, color]):
            console.print(
                "[red]Error: At least one field must be specified (--name, --description, or --color)[/red]"
            )
            sys.exit(1)

        # Update label
        label = client.update_label(
            label_id=label_id,
            name=name,
            description=description,
            color=color,
        )

        # Display success message
        console.print(f"[green]✓[/green] Updated label: {label.name} ({label.id})")

        # Format output
        if format == "json":
            format_labels_json([label])
        else:  # detail
            format_labels_table([label])

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
def delete_label(
    ctx: typer.Context,
    label_id: Annotated[str, typer.Argument(help="Label ID")],
    confirm: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompt (permanently deletes the label)",
        ),
    ] = False,
) -> None:
    """Delete (permanently remove) a label.

    Examples:
        linear labels delete <label-id>
        linear labels delete <label-id> --yes  # Skip confirmation
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Confirm deletion unless --yes flag is used
        if not confirm:
            proceed = typer.confirm(
                f"Are you sure you want to permanently delete label {label_id}?"
            )
            if not proceed:
                console.print("[yellow]Cancelled[/yellow]")
                sys.exit(0)

        # Delete label
        client.delete_label(label_id=label_id)

        # Display success message
        console.print(f"[green]✓[/green] Deleted label: {label_id}")

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("archive")
def archive_label(
    ctx: typer.Context,
    label_id: Annotated[str, typer.Argument(help="Label ID")],
) -> None:
    """Archive a label.

    Examples:
        linear labels archive <label-id>
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Archive label
        client.archive_label(label_id=label_id)

        # Display success message
        console.print(f"[green]✓[/green] Archived label: {label_id}")

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
