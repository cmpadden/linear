"""User formatters for Linear CLI."""

import json

from rich.console import Console
from rich.table import Table

from linear.models import User


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
