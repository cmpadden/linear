"""Roadmap formatters for Linear CLI."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from linear.models import Roadmap


def _display_pagination(
    console: Console, count: int, pagination_info: dict[str, Any]
) -> None:
    """Display pagination information.

    Args:
        console: Rich console
        count: Number of items in current page
        pagination_info: Pagination metadata
    """
    # Check if using --all mode (has startIndex means paging mode, not --all)
    if "startIndex" not in pagination_info:
        # --all mode was used
        console.print(
            f"\n[dim]Total: {pagination_info.get('totalFetched', count)} roadmap(s)[/dim]"
        )
    elif pagination_info.get("hasNextPage"):
        # More pages available
        start = pagination_info.get("startIndex", 1)
        end = pagination_info.get("endIndex", count)
        console.print(
            f"\n[dim]Showing {start}-{end} (more available, use --page to see more)[/dim]"
        )
    else:
        # Last page or only page
        if pagination_info.get("currentPage", 1) > 1:
            start = pagination_info.get("startIndex", 1)
            end = pagination_info.get("endIndex", count)
            console.print(f"\n[dim]Showing {start}-{end}[/dim]")
        else:
            console.print(f"\n[dim]Total: {count} roadmap(s)[/dim]")


def format_roadmaps_table(
    roadmaps: list[Roadmap], pagination_info: dict[str, Any] | None = None
) -> None:
    """Format roadmaps as a rich table.

    Args:
        roadmaps: List of Roadmap objects to display
        pagination_info: Optional pagination metadata
    """
    console = Console()

    if not roadmaps:
        console.print("[yellow]No roadmaps found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Name", style="bright_blue")
    table.add_column("Slug", style="cyan")
    table.add_column("Owner", style="magenta")
    table.add_column("Updated", style="dim")

    for roadmap in roadmaps:
        # Truncate name if too long
        name = roadmap.name
        if len(name) > 40:
            name = name[:37] + "..."

        table.add_row(
            name,
            roadmap.slug_id,
            roadmap.format_owner(),
            roadmap.format_updated_date(),
        )

    console.print(table)

    # Display pagination info
    if pagination_info:
        _display_pagination(console, len(roadmaps), pagination_info)
    else:
        console.print(f"\n[dim]Total: {len(roadmaps)} roadmap(s)[/dim]")


def format_roadmaps_json(roadmaps: list[Roadmap]) -> None:
    """Format roadmaps as JSON.

    Args:
        roadmaps: List of Roadmap objects to display
    """
    roadmaps_data = []
    for roadmap in roadmaps:
        # Use model_dump with by_alias=True to get camelCase field names
        roadmap_dict = roadmap.model_dump(mode="json", by_alias=True)
        roadmaps_data.append(roadmap_dict)

    print(
        json.dumps(
            {"roadmaps": roadmaps_data, "count": len(roadmaps)}, indent=2, default=str
        )
    )


def format_roadmap_detail(roadmap: Roadmap) -> None:
    """Format a single roadmap with full details.

    Args:
        roadmap: Roadmap Pydantic model
    """
    console = Console()

    # Header
    console.print(f"\n[bold bright_blue]{roadmap.name}[/bold bright_blue]")
    console.print(f"[dim]{roadmap.url}[/dim]\n")

    # Info
    console.print(f"[bold]Slug:[/bold] {roadmap.slug_id}")

    # People
    if roadmap.owner:
        console.print(
            f"[bold]Owner:[/bold] [magenta]{roadmap.owner.name}[/magenta] ({roadmap.owner.email})"
        )
    else:
        console.print("[bold]Owner:[/bold] No owner assigned")

    if roadmap.creator:
        console.print(
            f"[bold]Creator:[/bold] {roadmap.creator.name} ({roadmap.creator.email})"
        )

    # Dates
    console.print(f"\n[bold]Created:[/bold] {roadmap.format_date(roadmap.created_at)}")
    console.print(f"[bold]Updated:[/bold] {roadmap.format_updated_date()}")

    if roadmap.archived_at:
        console.print(
            f"[bold]Archived:[/bold] {roadmap.format_date(roadmap.archived_at)}"
        )

    # Description
    if roadmap.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(roadmap.description)


def format_roadmap_json(roadmap: Roadmap) -> None:
    """Format a single roadmap as JSON.

    Args:
        roadmap: Roadmap Pydantic model
    """
    roadmap_dict = roadmap.model_dump(mode="json", by_alias=True)
    print(json.dumps(roadmap_dict, indent=2, default=str))
