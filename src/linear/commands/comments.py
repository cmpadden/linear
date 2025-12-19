"""Comments commands for Linear CLI."""

import sys
import tempfile
import os
import subprocess
from typing_extensions import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.prompt import Prompt

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_comments_table,
    format_comments_json,
    format_comment_detail,
    format_comment_json,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear comments")


@app.command("list")
def list_comments(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """List comments on an issue.

    Examples:

      # List comments on an issue
      linear comments list ENG-123

      # Output as JSON
      linear comments list ENG-123 --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Resolve issue identifier to UUID
        issue = client.get_issue(issue_id)

        # Fetch comments
        comments, _ = client.list_comments(issue_id=issue.id, limit=250)

        # Format output
        if format == "json":
            format_comments_json(comments)
        else:  # table
            format_comments_table(comments)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("create")
def create_comment(
    ctx: typer.Context,
    issue_id: Annotated[
        str, typer.Argument(help="Issue ID or identifier (e.g., 'ENG-123')")
    ],
    body: Annotated[
        str | None,
        typer.Option("--body", "-b", help="Comment body (markdown)"),
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Add a comment to an issue.

    If --body is not provided, opens your $EDITOR to write the comment.

    Examples:

      # Create comment with body flag
      linear comments create ENG-123 --body "This looks good!"

      # Open editor to write comment
      linear comments create ENG-123

      # Output as JSON
      linear comments create ENG-123 --body "Comment" --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Resolve issue identifier to UUID
        issue = client.get_issue(issue_id)

        # Get comment body
        if body is None:
            # Open editor
            body = _open_editor_for_comment()

            if not body.strip():
                console.print("[yellow]Comment body is empty. Cancelled.[/yellow]")
                sys.exit(0)

        # Create comment
        comment = client.create_comment(issue_id=issue.id, body=body)

        # Format output
        if format == "json":
            format_comment_json(comment)
        else:  # detail
            console.print("\n[green]Comment created successfully[/green]")
            format_comment_detail(comment)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("update")
def update_comment(
    ctx: typer.Context,
    comment_id: Annotated[str, typer.Argument(help="Comment ID (UUID)")],
    body: Annotated[
        str | None,
        typer.Option("--body", "-b", help="New comment body (markdown)"),
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: detail, json")
    ] = "detail",
) -> None:
    """Update a comment.

    If --body is not provided, opens your $EDITOR to edit the comment.

    Examples:

      # Update comment with body flag
      linear comments update <comment-id> --body "Updated text"

      # Open editor to edit comment
      linear comments update <comment-id>

      # Output as JSON
      linear comments update <comment-id> --body "Text" --format json
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch existing comment
        existing_comment = client.get_comment(comment_id)

        # Get new comment body
        if body is None:
            # Open editor with existing body
            body = _open_editor_for_comment(existing_body=existing_comment.body)

            if not body.strip():
                console.print("[yellow]Comment body is empty. Cancelled.[/yellow]")
                sys.exit(0)

        # Update comment
        updated_comment = client.update_comment(comment_id=comment_id, body=body)

        # Format output
        if format == "json":
            format_comment_json(updated_comment)
        else:  # detail
            console.print("\n[green]Comment updated successfully[/green]")
            format_comment_detail(updated_comment)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@app.command("delete")
def delete_comment(
    ctx: typer.Context,
    comment_id: Annotated[str, typer.Argument(help="Comment ID (UUID)")],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Delete a comment.

    Examples:

      # Delete comment with confirmation
      linear comments delete <comment-id>

      # Delete without confirmation prompt
      linear comments delete <comment-id> --yes
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize
        client = LinearClient(verbose_logger=verbose_logger)
        console = Console()

        # Fetch the comment first to show details
        try:
            comment = client.get_comment(comment_id)
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(f"[dim]Make sure '{comment_id}' is a valid comment ID[/dim]")
            sys.exit(1)

        # Show comment details
        console.print("\n[bold]Comment to delete:[/bold]")
        console.print(f"  [bold]Author:[/bold] {comment.user.name}")
        console.print(
            f"  [bold]Created:[/bold] {comment.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        # Show truncated body
        body_preview = (
            comment.body[:100] + "..." if len(comment.body) > 100 else comment.body
        )
        console.print(f"  [bold]Body:[/bold] {body_preview}")

        # Confirmation (unless --yes flag is used)
        if not yes:
            response = Prompt.ask(
                "\n[yellow]Are you sure you want to delete this comment?[/yellow]",
                choices=["y", "yes", "n", "no"],
                default="n",
                show_choices=True,
                case_sensitive=False,
            )

            if response[0].lower() == "n":
                console.print("[yellow]Deletion cancelled.[/yellow]")
                sys.exit(0)

        # Delete the comment
        try:
            client.delete_comment(comment_id=comment_id)
            console.print("\n[green]Comment deleted successfully[/green]")
        except LinearClientError as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def _open_editor_for_comment(existing_body: str | None = None) -> str:
    """Open editor for writing/editing a comment.

    Args:
        existing_body: Existing comment body for editing (optional)

    Returns:
        Edited comment body

    Raises:
        FileNotFoundError: If editor not found
        RuntimeError: If editor fails
    """
    editor = os.environ.get("EDITOR", "vi")

    # Check if editor exists
    if (
        not subprocess.run(
            ["which", editor], capture_output=True, check=False
        ).returncode
        == 0
    ):
        raise FileNotFoundError(
            f"Editor '{editor}' not found in PATH. "
            f"Set EDITOR environment variable to your preferred editor."
        )

    # Create temp file with existing content
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="linear-comment-", delete=False
    ) as f:
        if existing_body:
            f.write(existing_body)
        temp_path = f.name

    try:
        # Run editor
        result = subprocess.run([editor, temp_path], check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Editor exited with code {result.returncode}")

        # Read back content
        with open(temp_path) as f:
            content = f.read()

        return content.strip()

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
