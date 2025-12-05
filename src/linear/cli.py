"""Linear CLI - Command line interface for Linear."""

from typing import Optional

import typer
from typing_extensions import Annotated

from linear import __version__
from linear.commands import cycles, issues, labels, projects, teams, users


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
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """Linear CLI - Interact with Linear from your terminal."""
    pass


# Register command modules
app.add_typer(issues.app, name="issues")
app.add_typer(issues.app, name="i", hidden=True)

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


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
