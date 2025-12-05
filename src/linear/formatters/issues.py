"""Issue formatters for Linear CLI."""

import json
from collections import defaultdict
from typing import Literal

from rich.console import Console
from rich.markup import escape
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
