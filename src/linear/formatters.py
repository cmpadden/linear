"""Output formatters for Linear CLI."""

import json
from collections import defaultdict
from typing import Literal

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from linear.models import Cycle, Issue, Label, Project, Team, User


def format_table(issues: list[Issue]) -> None:
    """Format issues as a rich table.

    Args:
        issues: List of Issue objects to display
    """
    console = Console()

    if not issues:
        console.print("[yellow]No issues found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("ID", style="bright_blue", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Assignee", style="magenta")
    table.add_column("Updated", style="dim")

    for issue in issues:
        # Truncate title if too long
        title = issue.title
        if len(title) > 50:
            title = title[:47] + "..."

        table.add_row(
            issue.format_short_id(),
            escape(title),
            issue.state.name,
            issue.priority_label,
            issue.format_assignee(),
            issue.format_updated_date(),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(issues)} issue(s)[/dim]")


def format_table_grouped(
    issues: list[Issue], group_by: Literal["cycle", "project", "team"]
) -> None:
    """Format issues as a rich table grouped by a specific field.

    Args:
        issues: List of Issue objects to display
        group_by: Field to group by (cycle, project, or team)
    """
    console = Console()

    if not issues:
        console.print("[yellow]No issues found.[/yellow]")
        return

    # Group issues
    groups: dict[str, list[Issue]] = defaultdict(list)
    for issue in issues:
        if group_by == "cycle":
            key = issue.cycle.name if issue.cycle and issue.cycle.name else "No cycle"
        elif group_by == "project":
            key = (
                issue.project.name
                if issue.project and issue.project.name
                else "No project"
            )
        elif group_by == "team":
            key = f"{issue.team.key} - {issue.team.name}"
        else:
            key = "Unknown"
        groups[key].append(issue)

    # Sort groups: "No cycle/project/team" goes last, then alphabetical
    sorted_groups = sorted(groups.items(), key=lambda x: (x[0].startswith("No "), x[0]))

    # Pre-calculate max widths for ALL columns across all issues
    max_id_width = max(len(issue.format_short_id()) for issue in issues)
    max_status_width = max(len(issue.state.name) for issue in issues)
    max_priority_width = max(len(issue.priority_label) for issue in issues)
    max_assignee_width = max(len(issue.format_assignee()) for issue in issues)
    max_updated_width = max(len(issue.format_updated_date()) for issue in issues)

    # Calculate title width based on terminal size
    # Account for fixed column widths + padding (2 per column * 5 = 10, excluding edges)
    terminal_width = console.width
    fixed_width = (
        max_id_width
        + max_status_width
        + max_priority_width
        + max_assignee_width
        + max_updated_width
        + 10
    )
    available_for_title = terminal_width - fixed_width
    # Cap title between reasonable min/max
    max_title_width = max(20, min(available_for_title, 70))

    # Display each group
    for group_name, group_issues in sorted_groups:
        console.print(
            f"\n[bold cyan]{group_name}[/bold cyan] [dim]({len(group_issues)} issue{'s' if len(group_issues) != 1 else ''})[/dim]"
        )

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 1),
            pad_edge=False,
            expand=False,
        )
        table.add_column(
            "ID",
            style="bright_blue",
            no_wrap=True,
            width=max_id_width,
        )
        table.add_column(
            "Title",
            style="white",
            no_wrap=True,
            overflow="ellipsis",
            width=max_title_width,
        )
        table.add_column(
            "Status",
            style="green",
            no_wrap=True,
            width=max_status_width,
        )
        table.add_column(
            "Priority",
            style="yellow",
            no_wrap=True,
            width=max_priority_width,
        )
        table.add_column(
            "Assignee",
            style="magenta",
            no_wrap=True,
            width=max_assignee_width,
        )
        table.add_column(
            "Updated",
            style="dim",
            no_wrap=True,
            width=max_updated_width,
        )

        for issue in group_issues:
            table.add_row(
                issue.format_short_id(),
                escape(issue.title),
                issue.state.name,
                issue.priority_label,
                issue.format_assignee(),
                issue.format_updated_date(),
            )

        console.print(table)

    console.print(
        f"\n[dim]Total: {len(issues)} issue(s) across {len(groups)} group(s)[/dim]"
    )


def format_json(issues: list[Issue]) -> None:
    """Format issues as JSON.

    Args:
        issues: List of Issue objects to display
    """
    issues_data = []
    for issue in issues:
        # Use model_dump with by_alias=True to get camelCase field names
        issue_dict = issue.model_dump(mode="json", by_alias=True)
        issues_data.append(issue_dict)

    print(
        json.dumps({"issues": issues_data, "count": len(issues)}, indent=2, default=str)
    )


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


def format_teams_table(teams: list[Team]) -> None:
    """Format teams as a rich table.

    Args:
        teams: List of Team objects to display
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


def format_issue_detail(issue: Issue) -> None:
    """Format a single issue with full details.

    Args:
        issue: Issue Pydantic model
    """
    console = Console()

    # Header
    console.print(
        f"\n[bold bright_blue]{issue.identifier}[/bold bright_blue]: {escape(issue.title)}"
    )
    console.print(f"[dim]{issue.url}[/dim]\n")

    # Status section
    console.print(f"[bold]Status:[/bold] [green]{issue.state.name}[/green]")
    console.print(f"[bold]Priority:[/bold] [yellow]{issue.priority_label}[/yellow]")

    # People
    if issue.assignee:
        console.print(
            f"[bold]Assignee:[/bold] [magenta]{issue.assignee.name}[/magenta] ({issue.assignee.email})"
        )
    else:
        console.print("[bold]Assignee:[/bold] Unassigned")

    if issue.creator:
        console.print(
            f"[bold]Creator:[/bold] {issue.creator.name} ({issue.creator.email})"
        )

    # Project & Team
    if issue.project:
        console.print(f"[bold]Project:[/bold] {issue.project.name}")

    console.print(f"[bold]Team:[/bold] {issue.team.name} ({issue.team.key})")

    # Cycle
    if issue.cycle:
        console.print(f"[bold]Cycle:[/bold] {issue.cycle.name} (#{issue.cycle.number})")

    # Dates
    console.print(f"\n[bold]Created:[/bold] {issue.format_created_date()}")
    console.print(f"[bold]Updated:[/bold] {issue.format_updated_date()}")

    if issue.due_date:
        console.print(f"[bold]Due Date:[/bold] {issue.due_date.strftime('%Y-%m-%d')}")

    if issue.completed_at:
        console.print(
            f"[bold]Completed:[/bold] {issue.completed_at.strftime('%Y-%m-%d')}"
        )

    # Estimate
    if issue.estimate:
        console.print(f"[bold]Estimate:[/bold] {issue.estimate} points")

    # Labels
    if issue.labels:
        label_names = [label.name for label in issue.labels]
        console.print(f"[bold]Labels:[/bold] {', '.join(label_names)}")

    # Parent issue
    if issue.parent:
        console.print(
            f"[bold]Parent:[/bold] {issue.parent.identifier} - {issue.parent.title}"
        )

    # Description
    if issue.description:
        console.print("\n[bold]Description:[/bold]")
        console.print(issue.description)

    # Comments
    if issue.comments:
        console.print(f"\n[bold]Comments ({len(issue.comments)}):[/bold]")
        for comment in issue.comments[:5]:  # Show first 5 comments
            console.print(
                f"\n[cyan]{comment.user.name}[/cyan] on {comment.created_at.strftime('%Y-%m-%d')}:"
            )
            console.print(comment.body[:200])  # Truncate long comments

    # Attachments
    if issue.attachments:
        console.print(f"\n[bold]Attachments ({len(issue.attachments)}):[/bold]")
        for attachment in issue.attachments:
            console.print(f"  • {attachment.title} - {attachment.url}")

    # Subscribers
    if issue.subscribers:
        sub_names = [sub.name for sub in issue.subscribers]
        console.print(f"\n[bold]Subscribers:[/bold] {', '.join(sub_names)}")


def format_issue_json(issue: Issue) -> None:
    """Format a single issue as JSON.

    Args:
        issue: Issue Pydantic model
    """
    issue_dict = issue.model_dump(mode="json", by_alias=True)
    print(json.dumps(issue_dict, indent=2, default=str))


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


def format_users_table(users: list[User]) -> None:
    """Format users as a rich table.

    Args:
        users: List of User objects to display
    """
    console = Console()

    if not users:
        console.print("[yellow]No users found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Name", style="bright_blue")
    table.add_column("Email", style="cyan")
    table.add_column("Role", style="yellow", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=True)
    table.add_column("Timezone", style="dim")
    table.add_column("Created", style="dim")

    for user in users:
        # Status with color coding
        if user.active:
            status = "[green]Active[/green]"
        else:
            status = "[dim]Inactive[/dim]"

        # Role with color coding
        if user.admin:
            role = "[yellow]Admin[/yellow]"
        else:
            role = "Member"

        # Truncate email if too long
        email = user.email
        if len(email) > 35:
            email = email[:32] + "..."

        table.add_row(
            user.display_name,
            email,
            role,
            status,
            user.timezone or "—",
            user.format_created_at(),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(users)} user(s)[/dim]")


def format_users_json(users: list[User]) -> None:
    """Format users as JSON.

    Args:
        users: List of User objects to display
    """
    users_data = []
    for user in users:
        # Use model_dump with by_alias=True to get camelCase field names
        user_dict = user.model_dump(mode="json", by_alias=True)
        users_data.append(user_dict)

    print(json.dumps({"users": users_data, "count": len(users)}, indent=2, default=str))


def format_user_detail(user: User) -> None:
    """Format a single user with full details.

    Args:
        user: User Pydantic model
    """
    console = Console()

    # Header
    console.print(f"\n[bold bright_blue]{user.display_name}[/bold bright_blue]")
    console.print(f"[dim]{user.email}[/dim]\n")

    # Status and role
    if user.active:
        status_display = "[green]✓ Active[/green]"
    else:
        status_display = "[dim]✗ Inactive[/dim]"

    role_display = "[yellow]Admin[/yellow]" if user.admin else "Member"

    console.print(f"[bold]Status:[/bold] {status_display}")
    console.print(f"[bold]Role:[/bold] {role_display}")

    # Organization
    if user.organization:
        console.print(f"[bold]Organization:[/bold] {user.organization.name}")

    # Timezone
    if user.timezone:
        console.print(f"[bold]Timezone:[/bold] {user.timezone}")

    # Status message
    if user.status_label:
        status_msg = (
            f"{user.status_emoji} {user.status_label}"
            if user.status_emoji
            else user.status_label
        )
        console.print(f"[bold]Status Message:[/bold] {status_msg}")

        if user.status_until_at:
            console.print(
                f"[dim]  (until {user.status_until_at.strftime('%Y-%m-%d')})[/dim]"
            )

    # Description
    if user.description:
        console.print("\n[bold]Bio:[/bold]")
        console.print(user.description)

    # Dates
    console.print(f"\n[bold]Joined:[/bold] {user.format_created_at()}")
    updated_date = (
        user.updated_at.strftime("%Y-%m-%d") if user.updated_at else "Unknown"
    )
    console.print(f"[bold]Last Updated:[/bold] {updated_date}")


def format_user_json(user: User) -> None:
    """Format a single user as JSON.

    Args:
        user: User Pydantic model
    """
    user_dict = user.model_dump(mode="json", by_alias=True)
    print(json.dumps(user_dict, indent=2, default=str))


def format_labels_table(labels: list[Label]) -> None:
    """Format labels as a rich table.

    Args:
        labels: List of Label objects
    """
    console = Console()
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )

    table.add_column("Name", style="cyan", min_width=20)
    table.add_column("Team", style="yellow", min_width=10)
    table.add_column("Color", style="white", min_width=10)
    table.add_column("Description", style="dim", min_width=30)

    for label in labels:
        # Format the color as a colored square
        color_display = f"[{label.color}]●[/] {label.color}"

        # Truncate description if too long
        description = label.description or ""
        if len(description) > 50:
            description = description[:47] + "..."

        table.add_row(
            label.name,
            label.format_team(),
            color_display,
            description,
        )

    console.print(table)
    console.print(
        f"\n[dim]Total: {len(labels)} label{'s' if len(labels) != 1 else ''}[/dim]"
    )


def format_labels_json(labels: list[Label]) -> None:
    """Format labels as JSON.

    Args:
        labels: List of Label objects
    """
    labels_data = []
    for label in labels:
        # Use model_dump with by_alias=True to get camelCase field names
        label_dict = label.model_dump(mode="json", by_alias=True)
        labels_data.append(label_dict)

    output = {"labels": labels_data, "count": len(labels)}
    print(json.dumps(output, indent=2, default=str))
