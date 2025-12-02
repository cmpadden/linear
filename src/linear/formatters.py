"""Output formatters for Linear CLI."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from linear.models import Issue, Project


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
    console.print(f"\n[bold bright_blue]{issue.get('identifier', 'N/A')}[/bold bright_blue]: {issue.get('title', 'Untitled')}")
    console.print(f"[dim]{issue.get('url', '')}[/dim]\n")

    # Status section
    state = issue.get("state", {})
    console.print(f"[bold]Status:[/bold] [green]{state.get('name', 'Unknown')}[/green]")
    console.print(f"[bold]Priority:[/bold] [yellow]{issue.get('priorityLabel', 'No priority')}[/yellow]")

    # People
    assignee = issue.get("assignee")
    if assignee:
        console.print(f"[bold]Assignee:[/bold] [magenta]{assignee.get('name')}[/magenta] ({assignee.get('email')})")
    else:
        console.print(f"[bold]Assignee:[/bold] Unassigned")

    creator = issue.get("creator")
    if creator:
        console.print(f"[bold]Creator:[/bold] {creator.get('name')} ({creator.get('email')})")

    # Project & Team
    project = issue.get("project")
    if project:
        console.print(f"[bold]Project:[/bold] {project.get('name')}")

    team = issue.get("team", {})
    console.print(f"[bold]Team:[/bold] {team.get('name')} ({team.get('key')})")

    # Cycle
    cycle = issue.get("cycle")
    if cycle:
        console.print(f"[bold]Cycle:[/bold] {cycle.get('name')} (#{cycle.get('number')})")

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
        console.print(f"[bold]Parent:[/bold] {parent.get('identifier')} - {parent.get('title')}")

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
                console.print(f"\n[cyan]{user.get('name', 'Unknown')}[/cyan] on {created}:")
                console.print(comment.get("body", "")[:200])  # Truncate long comments

    # Attachments
    attachments_data = issue.get("attachments") or {}
    attachments = attachments_data.get("nodes", [])
    if attachments:
        console.print(f"\n[bold]Attachments ({len(attachments)}):[/bold]")
        for attachment in attachments:
            if attachment:
                console.print(f"  • {attachment.get('title')} - {attachment.get('url')}")

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
