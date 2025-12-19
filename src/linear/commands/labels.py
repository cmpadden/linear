"""Labels commands for Linear CLI."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated
from pydantic import ValidationError

from linear.api import LinearClient, LinearClientError
from linear.formatters import (
    format_labels_json,
    format_labels_table,
)
from linear.utils import VerboseLogger

app = typer.Typer(help="Manage Linear labels", no_args_is_help=True)


@app.command("list")
def list_labels(
    ctx: typer.Context,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Maximum number of labels to return")
    ] = 50,
    team: Annotated[
        Optional[str],
        typer.Option(
            "--team", "-t", help="Filter by team ID or key (e.g., 'ENG', 'DESIGN')"
        ),
    ] = None,
    include_archived: Annotated[
        bool, typer.Option("--include-archived", help="Include archived labels")
    ] = False,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: table (default) or json"),
    ] = "table",
) -> None:
    """List issue labels.

    Examples:
        linear labels list
        linear labels list --team ENG
        linear labels list --limit 20 --format json
        linear labels list --include-archived
    """
    try:
        # Extract verbose flag from context
        verbose = ctx.obj.get("verbose", False) if ctx.obj else False
        verbose_logger = VerboseLogger(enabled=verbose)

        # Initialize client
        client = LinearClient(verbose_logger=verbose_logger)

        # Fetch labels
        labels = client.list_labels(
            limit=limit,
            team=team,
            include_archived=include_archived,
        )

        # Parse response

        # Format output
        if format == "json":
            format_labels_json(labels)
        else:  # table
            format_labels_table(labels)

    except LinearClientError as e:
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        typer.echo(f"Data validation error: {e.errors()[0]['msg']}", err=True)
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
