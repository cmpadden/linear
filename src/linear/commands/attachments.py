"""Attachments commands for Linear CLI."""

import sys

import typer
from pydantic import ValidationError
from rich.console import Console
from typing_extensions import Annotated

from linear.api import LinearClient, LinearClientError
from linear.formatters import attachments as attachments_formatter
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage issue attachments")


@app.command("list")
def list_attachments(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List all attachments for an issue.

    Examples:

      # List attachments for an issue
      linear attachments list ENG-123

      # Output as JSON
      linear attachments list ENG-123 --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch issue to resolve identifier to UUID
        issue = client.get_issue(issue_id)

        # Fetch attachments
        attachments = client.list_attachments(issue.id)

        # Format output
        if format == "json":
            attachments_formatter.format_json(attachments)
        else:  # table
            attachments_formatter.format_table(attachments)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("upload")
def upload_attachment(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    file_path: Annotated[str, typer.Argument(help="Path to file to upload")],
    title: Annotated[
        str | None,
        typer.Option("--title", "-t", help="Attachment title (defaults to filename)"),
    ] = None,
) -> None:
    """Upload a file attachment to an issue.

    Examples:

      # Upload a file
      linear attachments upload ENG-123 ./screenshot.png

      # Upload with custom title
      linear attachments upload ENG-123 ./doc.pdf --title "Design Document"
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch issue to resolve identifier to UUID
        console.print(f"[dim]Resolving issue {issue_id}...[/dim]")
        issue = client.get_issue(issue_id)

        # Upload attachment
        console.print(f"[dim]Uploading {file_path}...[/dim]")
        attachment = client.upload_attachment(
            issue_id=issue.id, file_path=file_path, title=title
        )

        # Success message
        console.print("\n[green]✓[/green] Attachment uploaded successfully!")
        console.print(f"[bold]Title:[/bold] {attachment.title}")
        console.print(f"[bold]URL:[/bold] {attachment.url}")
        console.print(f"[bold]Issue:[/bold] {issue.identifier}")

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command("delete")
def delete_attachment(
    ctx: typer.Context,
    attachment_id: Annotated[str, typer.Argument(help="Attachment ID")],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Delete an attachment.

    Examples:

      # Delete an attachment with confirmation
      linear attachments delete <attachment-id>

      # Delete without confirmation prompt
      linear attachments delete <attachment-id> --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Confirmation (unless --yes flag is used)
        if not yes:
            from rich.prompt import Prompt

            response = Prompt.ask(
                f"\n[yellow]Are you sure you want to delete attachment {attachment_id}?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="n",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]Deletion cancelled.[/yellow]")
                sys.exit(0)

        # Delete the attachment
        client.delete_attachment(attachment_id=attachment_id)
        console.print(
            f"\n[green]✓[/green] Attachment {attachment_id} deleted successfully"
        )

    except LinearClientError as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except ValidationError as e:
        console = Console()
        console.print(f"[red]Data validation error: {e.errors()[0]['msg']}[/red]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)
