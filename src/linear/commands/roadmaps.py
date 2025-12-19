"""Roadmaps commands for Linear CLI."""

import os
import subprocess
import sys
import tempfile
from typing import Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from typing_extensions import Annotated

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_roadmap_detail,
    format_roadmap_json,
    format_roadmaps_json,
    format_roadmaps_table,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear roadmaps")


def _open_editor(initial_text: str = "") -> str | None:
    """Open editor for text input.

    Args:
        initial_text: Initial text to populate editor with

    Returns:
        Edited text or None if empty

    Raises:
        FileNotFoundError: If editor not found
        RuntimeError: If editor fails
    """
    editor = os.environ.get("EDITOR", "vi")

    # Check if editor exists
    result = subprocess.run(
        ["which", editor], capture_output=True, check=False, text=True
    )
    if result.returncode != 0:
        raise FileNotFoundError(
            f"Editor '{editor}' not found in PATH. "
            f"Set EDITOR environment variable to your preferred editor."
        )

    # Create temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="linear-roadmap-", delete=False
    ) as f:
        f.write(initial_text)
        temp_path = f.name

    try:
        # Run editor
        result = subprocess.run([editor, temp_path], check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Editor exited with code {result.returncode}")

        # Read result
        with open(temp_path) as f:
            content = f.read()

        # Clean up comments and return
        lines = [
            line for line in content.split("\n") if not line.strip().startswith("#")
        ]
        text = "\n".join(lines).strip()
        return text if text else None

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.command("list")
def list_roadmaps(
    ctx: typer.Context,
    per_page: Annotated[
        int, typer.Option("--per-page", help="Number of roadmaps per page (max 250)")
    ] = 50,
    page: Annotated[
        Optional[int], typer.Option("--page", help="Page number to fetch (starts at 1)")
    ] = None,
    all: Annotated[
        bool, typer.Option("--all", help="Fetch all results automatically")
    ] = False,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived roadmaps")
    ] = False,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort by: created, updated")
    ] = "updated",
) -> None:
    """List Linear roadmaps.

    Examples:

      # List all roadmaps
      linear roadmaps list

      # Fetch all results
      linear roadmaps list --all

      # Pagination
      linear roadmaps list --page 2 --per-page 25

      # Output as JSON
      linear roadmaps list --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Validate per_page
        if per_page > 250:
            console.print("[red]Error: --per-page cannot exceed 250[/red]")
            sys.exit(1)

        # Calculate cursor for pagination
        after_cursor: str | None = None
        if page and page > 1:
            # For now, we need to iterate through pages to get the cursor
            current_page = 1
            while current_page < page:
                _, page_info = client.list_roadmaps(
                    limit=per_page,
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

        # Fetch roadmaps
        roadmaps, pagination_info = client.list_roadmaps(
            limit=per_page,
            include_archived=include_archived,
            sort=order_by,
            after=after_cursor,
            fetch_all=all,
        )

        # Enhance pagination info for display
        display_pagination_info: dict[str, str | bool | int] = dict(pagination_info)
        if not all:
            start_index = ((page or 1) - 1) * per_page + 1
            end_index = start_index + len(roadmaps) - 1
            display_pagination_info["startIndex"] = start_index
            display_pagination_info["endIndex"] = end_index
            display_pagination_info["currentPage"] = page or 1
            display_pagination_info["perPage"] = per_page

        # Format output
        if format == "json":
            format_roadmaps_json(roadmaps)
        else:  # table
            format_roadmaps_table(roadmaps, display_pagination_info)

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
def view_roadmap(
    ctx: typer.Context,
    roadmap_id: Annotated[str, typer.Argument(help="Roadmap ID or slug")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Get details of a specific Linear roadmap.

    Examples:

      # View roadmap by ID
      linear roadmaps view abc123-def456

       # View roadmap as JSON
       linear roadmaps view my-roadmap --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch roadmap
        roadmap = client.get_roadmap(roadmap_id)

        # Format output
        if format == "json":
            format_roadmap_json(roadmap)
        else:  # detail
            format_roadmap_detail(roadmap)

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
def create_roadmap(
    ctx: typer.Context,
    name: Annotated[
        Optional[str], typer.Option("--name", "-n", help="Roadmap name")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Roadmap description")
    ] = None,
    owner_id: Annotated[
        Optional[str], typer.Option("--owner-id", help="Owner user ID")
    ] = None,
    editor: Annotated[
        bool, typer.Option("--editor", "-e", help="Open editor for description")
    ] = False,
) -> None:
    """Create a new Linear roadmap.

    Examples:

      # Create roadmap with name
      linear roadmaps create --name "Q1 2024 Roadmap"

      # Create roadmap with description
      linear roadmaps create --name "Q1 2024" --description "Focus on core features"

      # Create roadmap with editor for description
      linear roadmaps create --name "Q1 2024" --editor

      # Create roadmap with owner
      linear roadmaps create --name "Q1 2024" --owner-id user-123
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Validate required fields
        if not name:
            console.print("[red]Error: --name is required[/red]")
            sys.exit(1)

        # Open editor for description if requested
        if editor and not description:
            description = _open_editor("# Enter roadmap description\n\n")
            if not description:
                console.print("[yellow]Description is empty[/yellow]")

        # Create roadmap (name is guaranteed to be str here after validation)
        assert name is not None  # Type narrowing for type checker
        roadmap = client.create_roadmap(
            name=name,
            description=description,
            owner_id=owner_id,
        )

        console.print(
            f"[green]✓[/green] Created roadmap: [bright_blue]{roadmap.name}[/bright_blue]"
        )
        console.print(f"  ID: {roadmap.id}")
        console.print(f"  Slug: {roadmap.slug_id}")
        console.print(f"  URL: {roadmap.url}")

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("update")
def update_roadmap(
    ctx: typer.Context,
    roadmap_id: Annotated[str, typer.Argument(help="Roadmap ID or slug")],
    name: Annotated[
        Optional[str], typer.Option("--name", "-n", help="New roadmap name")
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="New description")
    ] = None,
    owner_id: Annotated[
        Optional[str], typer.Option("--owner-id", help="New owner user ID")
    ] = None,
    editor: Annotated[
        bool, typer.Option("--editor", "-e", help="Open editor for description")
    ] = False,
) -> None:
    """Update an existing Linear roadmap.

    Examples:

      # Update roadmap name
      linear roadmaps update abc123 --name "Q2 2024 Roadmap"

      # Update description
      linear roadmaps update abc123 --description "Updated focus areas"

      # Update with editor
      linear roadmaps update abc123 --editor

      # Update owner
      linear roadmaps update abc123 --owner-id user-456
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Open editor for description if requested
        if editor:
            # Fetch current roadmap to pre-fill editor
            current_roadmap = client.get_roadmap(roadmap_id)
            current_description = current_roadmap.description or ""
            description = _open_editor(
                f"# Edit roadmap description\n\n{current_description}"
            )

        # Update roadmap
        roadmap = client.update_roadmap(
            roadmap_id=roadmap_id,
            name=name,
            description=description,
            owner_id=owner_id,
        )

        console.print(
            f"[green]✓[/green] Updated roadmap: [bright_blue]{roadmap.name}[/bright_blue]"
        )
        console.print(f"  ID: {roadmap.id}")
        console.print(f"  URL: {roadmap.url}")

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
