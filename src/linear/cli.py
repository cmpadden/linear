"""Linear CLI - Command line interface for Linear."""

from typing import Optional

import typer
from typing_extensions import Annotated

from linear import __version__
from linear.commands import (
    attachments,
    comments,
    cycles,
    issues,
    labels,
    projects,
    roadmaps,
    teams,
    users,
)


def version_callback(value: bool) -> None:
    """Callback for --version flag."""
    if value:
        typer.echo(f"Linear CLI version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    help="Linear CLI - Interact with Linear from your terminal", no_args_is_help=True
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show verbose output (GraphQL queries, response times)",
        ),
    ] = False,
) -> None:
    """Linear CLI - Interact with Linear from your terminal."""
    # Store verbose flag in context for all commands to access
    ctx.obj = {"verbose": verbose}


# Register command modules
app.add_typer(issues.app, name="issues")
app.add_typer(issues.app, name="i", hidden=True)

app.add_typer(attachments.app, name="attachments")

app.add_typer(comments.app, name="comments")

app.add_typer(projects.app, name="projects")
app.add_typer(projects.app, name="p", hidden=True)

app.add_typer(teams.app, name="teams")
app.add_typer(teams.app, name="t", hidden=True)

app.add_typer(cycles.app, name="cycles")
app.add_typer(cycles.app, name="c", hidden=True)

app.add_typer(users.app, name="users")
app.add_typer(users.app, name="u", hidden=True)

app.add_typer(labels.app, name="labels")
app.add_typer(labels.app, name="l", hidden=True)

app.add_typer(roadmaps.app, name="roadmaps")
app.add_typer(roadmaps.app, name="r", hidden=True)


@app.command()
def docs(ctx: typer.Context) -> None:
    """Generate comprehensive CLI documentation in Markdown format to stdout."""
    from typer.cli import get_docs_for_click

    click_obj = typer.main.get_command(app)

    docs = get_docs_for_click(
        obj=click_obj,
        ctx=ctx,
        name="linear",
        title="Linear CLI Documentation",
    )

    typer.echo(docs.strip())


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
