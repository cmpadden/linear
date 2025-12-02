"""Output formatters for Linear CLI."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from linear.models import Issue


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


def format_compact(issues: list[Issue]) -> None:
    """Format issues in compact single-line format.

    Args:
        issues: List of Issue objects to display
    """
    if not issues:
        print("No issues found.")
        return

    for issue in issues:
        assignee = issue.format_assignee()
        labels_str = f" [{issue.format_labels()}]" if issue.labels else ""
        project_str = f" ({issue.project_name})" if issue.project_name else ""

        print(
            f"{issue.format_short_id()}: {issue.title} - "
            f"{issue.state_name} | {issue.priority_label} | "
            f"{assignee}{project_str}{labels_str}"
        )

    print(f"\nTotal: {len(issues)} issue(s)")
