"""Output formatters for Linear CLI."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from linear.models import Issue, Project, Team


def format_table(issues: list[Issue]) -> None:
    """Format issues as a rich table.

    Args:
        issues: List of Issue objects to display
    """
    console = Console()

    if not issues:
        console.print("[yellow]No issues found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan")
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
            title,
            issue.state_name,
            issue.priority_label,
            issue.format_assignee(),
            issue.format_updated_date(),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(issues)} issue(s)[/dim]")


def format_json(issues: list[Issue]) -> None:
    """Format issues as JSON.

    Args:
        issues: List of Issue objects to display
    """
    issues_data = []
    for issue in issues:
        issues_data.append(
            {
                "id": issue.id,
                "identifier": issue.identifier,
                "title": issue.title,
                "description": issue.description,
                "priority": issue.priority,
                "priorityLabel": issue.priority_label,
                "url": issue.url,
                "createdAt": issue.created_at,
                "updatedAt": issue.updated_at,
                "completedAt": issue.completed_at,
                "state": {"name": issue.state_name, "type": issue.state_type},
                "assignee": (
                    {"name": issue.assignee_name, "email": issue.assignee_email}
                    if issue.assignee_name
                    else None
                ),
                "project": {"name": issue.project_name} if issue.project_name else None,
                "team": {"name": issue.team_name, "key": issue.team_key},
                "labels": issue.labels,
            }
        )

    print(json.dumps({"issues": issues_data, "count": len(issues)}, indent=2))


def format_projects_table(projects: list[Project]) -> None:
    """Format projects as a rich table.

    Args:
        projects: List of Project objects to display
    """
    console = Console()

    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan")
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
            project.team_key,
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
        projects_data.append(
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "state": project.state,
                "progress": project.progress,
                "startDate": project.start_date,
                "targetDate": project.target_date,
                "url": project.url,
                "createdAt": project.created_at,
                "updatedAt": project.updated_at,
                "archivedAt": project.archived_at,
                "color": project.color,
                "icon": project.icon,
                "lead": (
                    {"name": project.lead_name, "email": project.lead_email}
                    if project.lead_name
                    else None
                ),
                "team": {"name": project.team_name, "key": project.team_key},
            }
        )

    print(json.dumps({"projects": projects_data, "count": len(projects)}, indent=2))


def format_project_detail(project_data: dict) -> None:
    """Format a single project with full details.

    Args:
        project_data: Project data from API response
    """
    console = Console()
    project = project_data.get("project", {})

    if not project:
        console.print("[yellow]Project not found.[/yellow]")
        return

    # Header
    console.print(f"\n[bold bright_blue]{project.get('name', 'Untitled Project')}[/bold bright_blue]")
    console.print(f"[dim]{project.get('url', '')}[/dim]\n")

    # Status section
    state = project.get("state", "unknown")
    progress = project.get("progress", 0.0)
    console.print(f"[bold]State:[/bold] [green]{state.title()}[/green]")
    console.print(f"[bold]Progress:[/bold] [yellow]{progress * 100:.0f}%[/yellow]")

    # People
    lead = project.get("lead")
    if lead:
        console.print(f"[bold]Lead:[/bold] [magenta]{lead.get('name')}[/magenta] ({lead.get('email')})")
    else:
        console.print(f"[bold]Lead:[/bold] No lead assigned")

    creator = project.get("creator")
    if creator:
        console.print(f"[bold]Creator:[/bold] {creator.get('name')} ({creator.get('email')})")

    # Teams
    teams_data = project.get("teams", {}).get("nodes", [])
    if teams_data:
        team_names = [f"{team.get('name')} ({team.get('key')})" for team in teams_data]
        console.print(f"[bold]Teams:[/bold] {', '.join(team_names)}")

    # Members
    members_data = project.get("members", {}).get("nodes", [])
    if members_data:
        member_names = [member.get("name", "Unknown") for member in members_data[:10]]
        member_str = ", ".join(member_names)
        if len(members_data) > 10:
            member_str += f" and {len(members_data) - 10} more"
        console.print(f"[bold]Members:[/bold] {member_str}")

    # Dates
    console.print(f"\n[bold]Created:[/bold] {project.get('createdAt', 'Unknown')[:10]}")
    console.print(f"[bold]Updated:[/bold] {project.get('updatedAt', 'Unknown')[:10]}")

    if project.get("startDate"):
        console.print(f"[bold]Start Date:[/bold] {project.get('startDate')[:10]}")

    if project.get("targetDate"):
        console.print(f"[bold]Target Date:[/bold] {project.get('targetDate')[:10]}")

    if project.get("completedAt"):
        console.print(f"[bold]Completed:[/bold] {project.get('completedAt')[:10]}")

    if project.get("canceledAt"):
        console.print(f"[bold]Canceled:[/bold] {project.get('canceledAt')[:10]}")

    # Description
    description = project.get("description")
    if description:
        console.print(f"\n[bold]Description:[/bold]")
        console.print(description)

    # Issues
    issues_data = project.get("issues", {}).get("nodes", [])
    if issues_data:
        console.print(f"\n[bold]Issues ({len(issues_data)}):[/bold]")

        # Group by state type
        backlog = [i for i in issues_data if i.get("state", {}).get("type") == "backlog"]
        started = [i for i in issues_data if i.get("state", {}).get("type") == "started"]
        completed = [i for i in issues_data if i.get("state", {}).get("type") == "completed"]
        canceled = [i for i in issues_data if i.get("state", {}).get("type") == "canceled"]

        if backlog:
            console.print(f"\n  [dim]Backlog ({len(backlog)}):[/dim]")
            for issue in backlog[:5]:
                assignee_data = issue.get("assignee")
                assignee = assignee_data.get("name", "Unassigned") if assignee_data else "Unassigned"
                console.print(f"    • {issue.get('identifier')} - {issue.get('title', 'Untitled')[:50]} ({assignee})")

        if started:
            console.print(f"\n  [green]In Progress ({len(started)}):[/green]")
            for issue in started[:5]:
                assignee_data = issue.get("assignee")
                assignee = assignee_data.get("name", "Unassigned") if assignee_data else "Unassigned"
                console.print(f"    • {issue.get('identifier')} - {issue.get('title', 'Untitled')[:50]} ({assignee})")

        if completed:
            console.print(f"\n  [blue]Completed ({len(completed)}):[/blue]")
            for issue in completed[:3]:
                assignee_data = issue.get("assignee")
                assignee = assignee_data.get("name", "Unassigned") if assignee_data else "Unassigned"
                console.print(f"    • {issue.get('identifier')} - {issue.get('title', 'Untitled')[:50]} ({assignee})")

        if canceled:
            console.print(f"\n  [dim]Canceled ({len(canceled)}):[/dim]")


def format_project_json(project_data: dict) -> None:
    """Format a single project as JSON.

    Args:
        project_data: Project data from API response
    """
    print(json.dumps(project_data, indent=2))


def format_teams_table(teams: list[Team]) -> None:
    """Format teams as a rich table.

    Args:
        teams: List of Team objects to display
    """
    console = Console()

    if not teams:
        console.print("[yellow]No teams found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan")
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
            str(team.members_count),
            str(team.issues_count),
            str(team.projects_count),
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
        teams_data.append(
            {
                "id": team.id,
                "name": team.name,
                "key": team.key,
                "description": team.description,
                "color": team.color,
                "icon": team.icon,
                "private": team.private,
                "archived": team.archived,
                "createdAt": team.created_at,
                "updatedAt": team.updated_at,
                "membersCount": team.members_count,
                "issuesCount": team.issues_count,
                "projectsCount": team.projects_count,
                "cyclesEnabled": team.cycles_enabled,
            }
        )

    print(json.dumps({"teams": teams_data, "count": len(teams)}, indent=2))


def format_team_detail(team_data: dict) -> None:
    """Format a single team with full details.

    Args:
        team_data: Team data from API response
    """
    console = Console()
    team = team_data.get("team", {})

    if not team:
        console.print("[yellow]Team not found.[/yellow]")
        return

    # Header
    console.print(f"\n[bold bright_blue]{team.get('name', 'Untitled Team')} ({team.get('key', '')})[/bold bright_blue]")

    # Organization
    org = team.get("organization", {})
    if org:
        console.print(f"[dim]Organization: {org.get('name', '')}[/dim]\n")

    # Basic info
    console.print(f"[bold]Team Key:[/bold] {team.get('key', '')}")
    console.print(f"[bold]Private:[/bold] {'Yes' if team.get('private', False) else 'No'}")
    console.print(f"[bold]Cycles Enabled:[/bold] {'Yes' if team.get('cyclesEnabled', False) else 'No'}")

    timezone = team.get("timezone")
    if timezone:
        console.print(f"[bold]Timezone:[/bold] {timezone}")

    # Dates
    console.print(f"\n[bold]Created:[/bold] {team.get('createdAt', 'Unknown')[:10]}")
    console.print(f"[bold]Updated:[/bold] {team.get('updatedAt', 'Unknown')[:10]}")

    if team.get("archivedAt"):
        console.print(f"[bold]Archived:[/bold] {team.get('archivedAt')[:10]}")

    # Description
    description = team.get("description")
    if description:
        console.print(f"\n[bold]Description:[/bold]")
        console.print(description)

    # Members
    members_data = team.get("members", {}).get("nodes", [])
    if members_data:
        console.print(f"\n[bold]Members ({len(members_data)}):[/bold]")
        for member in members_data[:10]:
            name = member.get("displayName") or member.get("name", "Unknown")
            email = member.get("email", "")
            active_status = "" if member.get("active", True) else " [dim](inactive)[/dim]"
            admin_status = " [yellow](admin)[/yellow]" if member.get("admin", False) else ""
            console.print(f"  • {name} ({email}){admin_status}{active_status}")
        if len(members_data) > 10:
            console.print(f"  [dim]... and {len(members_data) - 10} more[/dim]")

    # Active Issues
    issues_data = team.get("issues", {}).get("nodes", [])
    if issues_data:
        console.print(f"\n[bold]Active Issues ({len(issues_data)}):[/bold]")
        for issue in issues_data[:10]:
            state_name = issue.get("state", {}).get("name", "Unknown")
            title = issue.get("title", "Untitled")[:50]
            assignee_data = issue.get("assignee")
            assignee = assignee_data.get("name", "Unassigned") if assignee_data else "Unassigned"
            priority = issue.get("priorityLabel", "No priority")
            console.print(f"  • {issue.get('identifier')} - {title}")
            console.print(f"    [dim]{state_name} | {priority} | {assignee}[/dim]")
        if len(issues_data) > 10:
            console.print(f"  [dim]... and {len(issues_data) - 10} more[/dim]")

    # Projects
    projects_data = team.get("projects", {}).get("nodes", [])
    if projects_data:
        console.print(f"\n[bold]Projects ({len(projects_data)}):[/bold]")
        for project in projects_data:
            name = project.get("name", "Untitled")
            state = project.get("state", "unknown").title()
            progress = project.get("progress", 0.0) * 100
            lead_data = project.get("lead")
            lead = lead_data.get("name", "No lead") if lead_data else "No lead"
            console.print(f"  • {name} - {state} ({progress:.0f}%) - Lead: {lead}")

    # Workflow States
    states_data = team.get("states", {}).get("nodes", [])
    if states_data:
        console.print(f"\n[bold]Workflow States ({len(states_data)}):[/bold]")
        # Group by type
        backlog = [s for s in states_data if s.get("type") == "backlog"]
        unstarted = [s for s in states_data if s.get("type") == "unstarted"]
        started = [s for s in states_data if s.get("type") == "started"]
        completed = [s for s in states_data if s.get("type") == "completed"]
        canceled = [s for s in states_data if s.get("type") == "canceled"]

        if backlog:
            state_names = [s.get("name", "") for s in backlog]
            console.print(f"  [dim]Backlog:[/dim] {', '.join(state_names)}")
        if unstarted:
            state_names = [s.get("name", "") for s in unstarted]
            console.print(f"  [yellow]Unstarted:[/yellow] {', '.join(state_names)}")
        if started:
            state_names = [s.get("name", "") for s in started]
            console.print(f"  [green]Started:[/green] {', '.join(state_names)}")
        if completed:
            state_names = [s.get("name", "") for s in completed]
            console.print(f"  [blue]Completed:[/blue] {', '.join(state_names)}")
        if canceled:
            state_names = [s.get("name", "") for s in canceled]
            console.print(f"  [dim]Canceled:[/dim] {', '.join(state_names)}")

    # Labels
    labels_data = team.get("labels", {}).get("nodes", [])
    if labels_data:
        label_names = [label.get("name", "") for label in labels_data[:20]]
        label_str = ", ".join(label_names)
        if len(labels_data) > 20:
            label_str += f" and {len(labels_data) - 20} more"
        console.print(f"\n[bold]Labels ({len(labels_data)}):[/bold] {label_str}")


def format_team_json(team_data: dict) -> None:
    """Format a single team as JSON.

    Args:
        team_data: Team data from API response
    """
    print(json.dumps(team_data, indent=2))


def format_issue_detail(issue_data: dict) -> None:
    """Format a single issue with full details.

    Args:
        issue_data: Issue data from API response
    """
    console = Console()
    issue = issue_data.get("issue", {})

    if not issue:
        console.print("[yellow]Issue not found.[/yellow]")
        return

    # Header
    console.print(
        f"\n[bold bright_blue]{issue.get('identifier', 'N/A')}[/bold bright_blue]: {issue.get('title', 'Untitled')}"
    )
    console.print(f"[dim]{issue.get('url', '')}[/dim]\n")

    # Status section
    state = issue.get("state", {})
    console.print(f"[bold]Status:[/bold] [green]{state.get('name', 'Unknown')}[/green]")
    console.print(
        f"[bold]Priority:[/bold] [yellow]{issue.get('priorityLabel', 'No priority')}[/yellow]"
    )

    # People
    assignee = issue.get("assignee")
    if assignee:
        console.print(
            f"[bold]Assignee:[/bold] [magenta]{assignee.get('name')}[/magenta] ({assignee.get('email')})"
        )
    else:
        console.print(f"[bold]Assignee:[/bold] Unassigned")

    creator = issue.get("creator")
    if creator:
        console.print(
            f"[bold]Creator:[/bold] {creator.get('name')} ({creator.get('email')})"
        )

    # Project & Team
    project = issue.get("project")
    if project:
        console.print(f"[bold]Project:[/bold] {project.get('name')}")

    team = issue.get("team", {})
    console.print(f"[bold]Team:[/bold] {team.get('name')} ({team.get('key')})")

    # Cycle
    cycle = issue.get("cycle")
    if cycle:
        console.print(
            f"[bold]Cycle:[/bold] {cycle.get('name')} (#{cycle.get('number')})"
        )

    # Dates
    console.print(f"\n[bold]Created:[/bold] {issue.get('createdAt', 'Unknown')[:10]}")
    console.print(f"[bold]Updated:[/bold] {issue.get('updatedAt', 'Unknown')[:10]}")

    if issue.get("dueDate"):
        console.print(f"[bold]Due Date:[/bold] {issue.get('dueDate')[:10]}")

    if issue.get("completedAt"):
        console.print(f"[bold]Completed:[/bold] {issue.get('completedAt')[:10]}")

    # Estimate
    if issue.get("estimate"):
        console.print(f"[bold]Estimate:[/bold] {issue.get('estimate')} points")

    # Labels
    labels = issue.get("labels", {}).get("nodes", [])
    if labels:
        label_names = [label.get("name") for label in labels]
        console.print(f"[bold]Labels:[/bold] {', '.join(label_names)}")

    # Parent issue
    parent = issue.get("parent")
    if parent:
        console.print(
            f"[bold]Parent:[/bold] {parent.get('identifier')} - {parent.get('title')}"
        )

    # Description
    description = issue.get("description")
    if description:
        console.print(f"\n[bold]Description:[/bold]")
        console.print(description)

    # Comments
    comments_data = issue.get("comments") or {}
    comments = comments_data.get("nodes", [])
    if comments:
        console.print(f"\n[bold]Comments ({len(comments)}):[/bold]")
        for comment in comments[:5]:  # Show first 5 comments
            if comment:
                user = comment.get("user") or {}
                created = comment.get("createdAt", "")[:10]
                console.print(
                    f"\n[cyan]{user.get('name', 'Unknown')}[/cyan] on {created}:"
                )
                console.print(comment.get("body", "")[:200])  # Truncate long comments

    # Attachments
    attachments_data = issue.get("attachments") or {}
    attachments = attachments_data.get("nodes", [])
    if attachments:
        console.print(f"\n[bold]Attachments ({len(attachments)}):[/bold]")
        for attachment in attachments:
            if attachment:
                console.print(
                    f"  • {attachment.get('title')} - {attachment.get('url')}"
                )

    # Subscribers
    subscribers_data = issue.get("subscribers") or {}
    subscribers = subscribers_data.get("nodes", [])
    if subscribers:
        sub_names = [sub.get("name", "Unknown") for sub in subscribers if sub]
        console.print(f"\n[bold]Subscribers:[/bold] {', '.join(sub_names)}")


def format_issue_json(issue_data: dict) -> None:
    """Format a single issue as JSON.

    Args:
        issue_data: Issue data from API response
    """
    print(json.dumps(issue_data, indent=2))
