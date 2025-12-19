"""Attachment formatters for Linear CLI."""

import json

from rich.console import Console
from rich.table import Table

from linear.models.attachments import Attachment


def format_table(attachments: list[Attachment]) -> None:
    """Format attachments as a rich table.

    Args:
        attachments: List of Attachment objects to display
    """
    console = Console()

    if not attachments:
        console.print("[yellow]No attachments found.[/yellow]")
        return

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=None,
        padding=(0, 1),
        pad_edge=False,
    )
    table.add_column("Title", style="cyan")
    table.add_column("URL", style="blue", no_wrap=True)
    table.add_column("Created", style="dim", no_wrap=True)

    for attachment in attachments:
        created_date = attachment.created_at.strftime("%Y-%m-%d")
        table.add_row(
            attachment.title,
            str(attachment.url),
            created_date,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(attachments)} attachment(s)[/dim]")


def format_json(attachments: list[Attachment]) -> None:
    """Format attachments as JSON.

    Args:
        attachments: List of Attachment objects to display
    """
    attachments_data = []
    for attachment in attachments:
        # Use model_dump with by_alias=True to get camelCase field names
        attachment_dict = attachment.model_dump(mode="json", by_alias=True)
        attachments_data.append(attachment_dict)

    print(
        json.dumps(
            {"attachments": attachments_data, "count": len(attachments)},
            indent=2,
            default=str,
        )
    )
