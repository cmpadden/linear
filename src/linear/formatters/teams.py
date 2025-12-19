"""Team formatters for Linear CLI."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from linear.models import Team


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
            f"\n[dim]Total: {pagination_info.get('totalFetched', count)} team(s)[/dim]"
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
            console.print(f"\n[dim]Total: {count} team(s)[/dim]")


def format_teams_table(
    teams: list[Team], pagination_info: dict[str, Any] | None = None
) -> None:
    """Format teams as a rich table.

    Args:
        teams: List of Team objects to display
        pagination_info: Optional pagination metadata
    """
    console = Console()

    if not teams:
        console.print("[yellow]No teams found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Key", style="bright_blue", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Members", style="magenta")
    table.add_column("Issues", style="yellow")
    table.add_column("Projects", style="green")
    table.add_column("Cycles", style="cyan")
    table.add_column("Updated", style="dim")

    for team in teams:
        # Truncate name if too long
        name = team.name
        if len(name) > 40:
            name = name[:37] + "..."

        cycles_status = "Yes" if team.cycles_enabled else "No"

        table.add_row(
            team.key,
            name,
            "0",  # members_count not in model
            "0",  # issues_count not in model
            "0",  # projects_count not in model
            cycles_status,
            team.format_updated_date(),
        )

    console.print(table)

    # Display pagination info
    if pagination_info:
        _display_pagination(console, len(teams), pagination_info)
    else:
        console.print(f"\n[dim]Total: {len(teams)} team(s)[/dim]")


def format_teams_json(teams: list[Team]) -> None:
    """Format teams as JSON.

    Args:
        teams: List of Team objects to display
    """
    teams_data = []
    for team in teams:
        # Use model_dump with by_alias=True to get camelCase field names
        team_dict = team.model_dump(mode="json", by_alias=True)
        teams_data.append(team_dict)

    print(json.dumps({"teams": teams_data, "count": len(teams)}, indent=2, default=str))


def format_team_detail(team: Team) -> None:
    """Format a single team with full details.

    Args:
        team: Team Pydantic model
    """
    console = Console()

    # Header
    console.print(f"\n[bold bright_blue]{team.name} ({team.key})[/bold bright_blue]")

    # Organization
    if team.organization:
        console.print(f"[dim]Organization: {team.organization.name}[/dim]\n")

    # Basic info
    console.print(f"[bold]Team Key:[/bold] {team.key}")
    console.print(f"[bold]Private:[/bold] {'Yes' if team.private else 'No'}")
    console.print(
        f"[bold]Cycles Enabled:[/bold] {'Yes' if team.cycles_enabled else 'No'}"
    )

    if team.timezone:
        console.print(f"[bold]Timezone:[/bold] {team.timezone}")

    # Dates
    created_date = (
        team.created_at.strftime("%Y-%m-%d") if team.created_at else "Unknown"
    )
    console.print(f"\n[bold]Created:[/bold] {created_date}")
    console.print(f"[bold]Updated:[/bold] {team.format_updated_date()}")

    if team.archived_at:
        console.print(f"[bold]Archived:[/bold] {team.archived_at.strftime('%Y-%m-%d')}")

    # Description
    if team.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(team.description)


def format_team_json(team: Team) -> None:
    """Format a single team as JSON.

    Args:
        team: Team Pydantic model
    """
    team_dict = team.model_dump(mode="json", by_alias=True)
    print(json.dumps(team_dict, indent=2, default=str))
