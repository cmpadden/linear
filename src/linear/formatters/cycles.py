"""Cycle formatters for Linear CLI."""

import json

from rich.console import Console
from rich.table import Table

from linear.models import Cycle


def format_cycles_table(cycles: list[Cycle]) -> None:
    """Format cycles as a rich table.

    Args:
        cycles: List of Cycle objects to display
    """
    console = Console()

    if not cycles:
        console.print("[yellow]No cycles found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Team", style="cyan", no_wrap=True)
    table.add_column("Name", style="bright_blue")
    table.add_column("Number", style="white", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Progress", style="yellow")
    table.add_column("Issues", style="magenta", no_wrap=True)
    table.add_column("Starts", style="dim")
    table.add_column("Ends", style="dim")

    for cycle in cycles:
        # Truncate name if too long
        name = cycle.name or "Untitled"
        if len(name) > 30:
            name = name[:27] + "..."

        # Status with color coding
        if cycle.is_active:
            status = "[green]Active[/green]"
        elif cycle.is_future:
            status = "[blue]Future[/blue]"
        elif cycle.is_past:
            status = "[dim]Past[/dim]"
        else:
            status = "Unknown"

        table.add_row(
            cycle.team.key,
            name,
            f"#{cycle.number}",
            status,
            cycle.format_progress(),
            "0",  # issues_count not in model
            cycle.format_starts_at(),
            cycle.format_ends_at(),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(cycles)} cycle(s)[/dim]")


def format_cycles_json(cycles: list[Cycle]) -> None:
    """Format cycles as JSON.

    Args:
        cycles: List of Cycle objects to display
    """
    cycles_data = []
    for cycle in cycles:
        # Use model_dump with by_alias=True to get camelCase field names
        cycle_dict = cycle.model_dump(mode="json", by_alias=True)
        cycles_data.append(cycle_dict)

    print(
        json.dumps({"cycles": cycles_data, "count": len(cycles)}, indent=2, default=str)
    )


def format_cycle_detail(cycle: Cycle) -> None:
    """Format a single cycle with full details.

    Args:
        cycle: Cycle Pydantic model
    """
    console = Console()

    # Header
    console.print(
        f"\n[bold bright_blue]{cycle.name}[/bold bright_blue] "
        f"[dim](Cycle #{cycle.number})[/dim]"
    )
    console.print(f"[dim]Team: {cycle.team.name} ({cycle.team.key})[/dim]\n")

    # Status section with visual indicator
    if cycle.is_active:
        status_display = "[green]🟢 Active[/green]"
    elif cycle.is_future:
        status_display = "[blue]🔵 Future[/blue]"
    elif cycle.is_past:
        status_display = "[dim]⚪ Past[/dim]"
    else:
        status_display = "Unknown"

    console.print(f"[bold]Status:[/bold] {status_display}")

    # Progress bar visualization
    progress_pct = cycle.progress * 100
    bar_width = 30
    filled = int(bar_width * cycle.progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    console.print(f"[bold]Progress:[/bold] [yellow]{bar}[/yellow] {progress_pct:.1f}%")

    # Dates section
    console.print(f"\n[bold]Start Date:[/bold] {cycle.format_starts_at()}")
    console.print(f"[bold]End Date:[/bold] {cycle.format_ends_at()}")

    if cycle.completed_at:
        console.print(
            f"[bold]Completed:[/bold] {cycle.format_date(cycle.completed_at)}"
        )

    # Metadata
    console.print(f"\n[bold]Created:[/bold] {cycle.format_date(cycle.created_at)}")
    console.print(f"[bold]Updated:[/bold] {cycle.format_date(cycle.updated_at)}")

    if cycle.archived_at:
        console.print(f"[bold]Archived:[/bold] {cycle.format_date(cycle.archived_at)}")

    # Special flags
    flags = []
    if cycle.is_next:
        flags.append("Next Cycle")
    if cycle.is_previous:
        flags.append("Previous Cycle")
    if flags:
        console.print(f"[bold]Tags:[/bold] {', '.join(flags)}")

    # Description
    if cycle.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(cycle.description)

    # Scope history (if available)
    if cycle.scope_history:
        console.print(
            f"\n[bold]Scope History:[/bold] {len(cycle.scope_history)} data points"
        )

    if cycle.issue_count_history:
        console.print(
            f"[bold]Issue Count History:[/bold] {len(cycle.issue_count_history)} data points"
        )


def format_cycle_json(cycle: Cycle) -> None:
    """Format a single cycle as JSON.

    Args:
        cycle: Cycle Pydantic model
    """
    cycle_dict = cycle.model_dump(mode="json", by_alias=True)
    print(json.dumps(cycle_dict, indent=2, default=str))
