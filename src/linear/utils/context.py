"""CLI context utilities for verbose output and logging."""

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


class VerboseLogger:
    """Helper for verbose CLI output."""

    def __init__(self, enabled: bool = False):
        """Initialize the verbose logger.

        Args:
            enabled: Whether verbose logging is enabled
        """
        self.enabled = enabled
        self.console = Console(stderr=True)  # Always output to stderr

    def log_graphql_query(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> None:
        """Log a GraphQL query with syntax highlighting.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Optional name for the operation (e.g., "list_issues")
        """
        if not self.enabled:
            return

        title = (
            f"GraphQL Query: {operation_name}" if operation_name else "GraphQL Query"
        )

        # Format GraphQL query with syntax highlighting
        syntax = Syntax(query.strip(), "graphql", theme="monokai", line_numbers=False)
        self.console.print(Panel(syntax, title=title, border_style="blue"))

        # Show variables if present
        if variables:
            vars_json = json.dumps(variables, indent=2)
            vars_syntax = Syntax(vars_json, "json", theme="monokai", line_numbers=False)
            self.console.print(
                Panel(vars_syntax, title="Variables", border_style="cyan")
            )

        self.console.print()  # Empty line for spacing

    def log_response_time(self, duration_ms: float) -> None:
        """Log API response time.

        Args:
            duration_ms: Response time in milliseconds
        """
        if not self.enabled:
            return

        self.console.print(f"[dim]⏱  Response time: {duration_ms:.2f}ms[/dim]\n")
