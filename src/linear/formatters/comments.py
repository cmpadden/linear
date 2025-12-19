"""Comment formatters for Linear CLI."""

import json

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from linear.models.comments import Comment


def format_table(comments: list[Comment]) -> None:
    """Format comments as a rich table.

    Args:
        comments: List of Comment objects to display
    """
    console = Console()

    if not comments:
        console.print("[yellow]No comments found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Author", style="cyan", no_wrap=True)
    table.add_column("Comment", style="white")
    table.add_column("Created", style="dim", no_wrap=True)

    for comment in comments:
        # Truncate body if too long
        body = comment.body.replace("\n", " ")  # Single line
        if len(body) > 80:
            body = body[:77] + "..."

        table.add_row(
            comment.user.name,
            escape(body),
            comment.format_created_date(),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(comments)} comment(s)[/dim]")


def format_json(comments: list[Comment]) -> None:
    """Format comments as JSON.

    Args:
        comments: List of Comment objects to display
    """
    comments_data = []
    for comment in comments:
        # Use model_dump with by_alias=True to get camelCase field names
        comment_dict = comment.model_dump(mode="json", by_alias=True)
        comments_data.append(comment_dict)

    print(
        json.dumps(
            {"comments": comments_data, "count": len(comments)}, indent=2, default=str
        )
    )


def format_comment_detail(comment: Comment) -> None:
    """Format a single comment with full details.

    Args:
        comment: Comment Pydantic model
    """
    console = Console()

    # Header
    console.print(f"\n[bold cyan]{comment.user.name}[/bold cyan]")
    console.print(
        f"[dim]{comment.user.email} • {comment.format_created_date()}[/dim]\n"
    )

    # Body
    console.print(comment.body)

    # Edit timestamp if available
    if comment.edited_at:
        console.print(
            f"\n[dim]Edited: {comment.edited_at.strftime('%Y-%m-%d %H:%M')}[/dim]"
        )


def format_comment_json(comment: Comment) -> None:
    """Format a single comment as JSON.

    Args:
        comment: Comment Pydantic model
    """
    comment_dict = comment.model_dump(mode="json", by_alias=True)
    print(json.dumps(comment_dict, indent=2, default=str))
