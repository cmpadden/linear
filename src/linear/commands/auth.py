"""Login, logout, and authentication status commands."""

import json
import os
from typing import Annotated

import typer
from rich.console import Console

from linear.api import LinearClient, LinearClientError
from linear.auth import (
    AuthError,
    browser_login,
    logout as clear_login,
    save_credentials,
)

app = typer.Typer(help="Inspect authentication", no_args_is_help=True)
console = Console()


def login(
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            min=1,
            max=600,
            help="Seconds to wait for browser authorization.",
        ),
    ] = 180,
) -> None:
    """Sign in through your browser and save OAuth tokens in the OS keychain.

    Uses PKCE without a client secret. Requests read/write access as you, not
    as an application user. The temporary callback listens on localhost:8765.
    An existing saved login is replaced only after the new login is validated.
    LINEAR_API_KEY, when set, still overrides the saved login for other commands.

    Args:
        timeout: Seconds to wait for the browser callback (1–600).
    """
    try:
        console.print("Opening Linear in your browser…")
        credentials = browser_login(
            lambda url: typer.echo(f"If the browser does not open, visit:\n{url}"),
            timeout=timeout,
        )
        # An explicit OAuth token deliberately bypasses LINEAR_API_KEY.
        viewer = LinearClient(access_token=credentials.access_token).get_viewer()[
            "viewer"
        ]
        save_credentials(credentials)
        console.print(
            f"Logged in as {viewer['name']} ({viewer['email']}).", markup=False
        )
        if os.getenv("LINEAR_API_KEY"):
            console.print(
                "[yellow]LINEAR_API_KEY is set and overrides this login. "
                "Unset it to use OAuth.[/yellow]"
            )
    except (AuthError, LinearClientError) as exc:
        console.print(f"Error: {exc}", style="red", markup=False)
        raise typer.Exit(1) from exc


def logout() -> None:
    """Revoke the saved OAuth login and delete its tokens from the OS keychain.

    Local tokens are deleted even if revocation fails. Does not change the
    LINEAR_API_KEY environment variable or revoke personal API keys.
    """
    try:
        existed, revoked = clear_login()
        if not existed:
            console.print("No saved OAuth login.")
        else:
            console.print("Saved OAuth login removed.")
            if not revoked:
                console.print(
                    "[yellow]Remote revocation could not be confirmed. "
                    "Revoke the application in Linear settings if needed.[/yellow]"
                )
        if os.getenv("LINEAR_API_KEY"):
            console.print(
                "[yellow]LINEAR_API_KEY is still set; commands will continue "
                "to use it.[/yellow]"
            )
    except AuthError as exc:
        console.print(f"Error: {exc}", style="red", markup=False)
        raise typer.Exit(1) from exc


@app.command("status")
def status(
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: table, json")
    ] = "table",
) -> None:
    """Verify the active credential and show its source and signed-in identity.

    Never displays tokens. LINEAR_API_KEY takes precedence over saved OAuth.
    Saved OAuth tokens are refreshed automatically when needed. Exits with
    code 1 if authentication fails or no usable credentials are available.

    Args:
        format: Output format, either table or json.
    """
    if format not in {"table", "json"}:
        console.print("Error: --format must be table or json", style="red")
        raise typer.Exit(1)
    source = "LINEAR_API_KEY" if os.getenv("LINEAR_API_KEY") else "OS keychain (OAuth)"
    try:
        viewer = LinearClient().get_viewer()["viewer"]
    except LinearClientError as exc:
        if format == "json":
            typer.echo(
                json.dumps(
                    {"authenticated": False, "source": source, "error": str(exc)}
                )
            )
        else:
            console.print(f"Error: {exc}", style="red", markup=False)
        raise typer.Exit(1) from exc
    payload = {
        "authenticated": True,
        "source": source,
        "user": {key: viewer[key] for key in ("id", "name", "email")},
    }
    if format == "json":
        typer.echo(json.dumps(payload))
    else:
        console.print(f"Credential source: {source}", markup=False)
        console.print(
            f"Logged in as {viewer['name']} ({viewer['email']}).", markup=False
        )
