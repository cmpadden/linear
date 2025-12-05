"""Project formatters for Linear CLI."""

import json

from rich.console import Console
from rich.table import Table

from linear.models import Project


def format_projects_table(projects: list[Project]) -> None:
    """Format projects as a rich table.

    Args:
        projects: List of Project objects to display
    """
    console = Console()

    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Name", style="bright_blue")
    table.add_column("State", style="green")
    table.add_column("Progress", style="yellow")
    table.add_column("Lead", style="magenta")
    table.add_column("Team", style="cyan")
    table.add_column("Target Date", style="dim")

    for project in projects:
        # Truncate name if too long
        name = project.name
        if len(name) > 40:
            name = name[:37] + "..."

        table.add_row(
            name,
            project.state.title(),
            project.format_progress(),
            project.format_lead(),
            project.teams[0].key if project.teams else "",
            project.format_target_date(),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(projects)} project(s)[/dim]")


def format_projects_json(projects: list[Project]) -> None:
    """Format projects as JSON.

    Args:
        projects: List of Project objects to display
    """
    projects_data = []
    for project in projects:
        # Use model_dump with by_alias=True to get camelCase field names
        project_dict = project.model_dump(mode="json", by_alias=True)
        projects_data.append(project_dict)

    print(
        json.dumps(
            {"projects": projects_data, "count": len(projects)}, indent=2, default=str
        )
    )


def format_project_detail(project: Project) -> None:
    """Format a single project with full details.

    Args:
        project: Project Pydantic model
    """
    console = Console()

    # Header
    console.print(f"\n[bold bright_blue]{project.name}[/bold bright_blue]")
    console.print(f"[dim]{project.url}[/dim]\n")

    # Status section
    console.print(f"[bold]State:[/bold] [green]{project.state.title()}[/green]")
    console.print(
        f"[bold]Progress:[/bold] [yellow]{project.format_progress()}[/yellow]"
    )

    # People
    if project.lead:
        console.print(
            f"[bold]Lead:[/bold] [magenta]{project.lead.name}[/magenta] ({project.lead.email})"
        )
    else:
        console.print("[bold]Lead:[/bold] No lead assigned")

    if project.creator:
        console.print(
            f"[bold]Creator:[/bold] {project.creator.name} ({project.creator.email})"
        )

    # Teams
    if project.teams:
        team_names = [f"{team.name} ({team.key})" for team in project.teams]
        console.print(f"[bold]Teams:[/bold] {', '.join(team_names)}")

    # Dates
    console.print(f"\n[bold]Created:[/bold] {project.format_date(project.created_at)}")
    console.print(f"[bold]Updated:[/bold] {project.format_updated_date()}")

    if project.start_date:
        console.print(f"[bold]Start Date:[/bold] {project.format_start_date()}")

    if project.target_date:
        console.print(f"[bold]Target Date:[/bold] {project.format_target_date()}")

    if project.completed_at:
        console.print(
            f"[bold]Completed:[/bold] {project.format_date(project.completed_at)}"
        )

    if project.canceled_at:
        console.print(
            f"[bold]Canceled:[/bold] {project.format_date(project.canceled_at)}"
        )

    # Description
    if project.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(project.description)


def format_project_json(project: Project) -> None:
    """Format a single project as JSON.

    Args:
        project: Project Pydantic model
    """
    project_dict = project.model_dump(mode="json", by_alias=True)
    print(json.dumps(project_dict, indent=2, default=str))
