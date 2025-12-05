"""Label formatters for Linear CLI."""

import json

from rich.console import Console
from rich.table import Table

from linear.models import Label


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
