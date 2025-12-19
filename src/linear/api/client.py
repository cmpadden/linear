"""Base Linear API client for GraphQL interactions."""

import os
import time
from typing import Any, TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from linear.utils.context import VerboseLogger


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


class LinearClient:
    """Client for interacting with the Linear GraphQL API."""

    API_URL = "https://api.linear.app/graphql"
    RATE_LIMIT = 1500  # requests per hour

    def __init__(
        self, api_key: str | None = None, verbose_logger: "VerboseLogger | None" = None
    ):
        """Initialize the Linear client.

        Args:
            api_key: Linear API key. If not provided, will read from LINEAR_API_KEY env var.
            verbose_logger: Optional logger for verbose output.

        Raises:
            LinearClientError: If no API key is provided or found.
        """
        self.api_key = api_key or os.getenv("LINEAR_API_KEY")
        if not self.api_key:
            raise LinearClientError(
                "No API key provided. Set LINEAR_API_KEY environment variable or pass api_key parameter.\n"
                "Get your API key at: https://linear.app/settings/api"
            )

        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        # Store verbose logger (import here to avoid circular dependency)
        if verbose_logger is None:
            from linear.utils.context import VerboseLogger

            verbose_logger = VerboseLogger(enabled=False)
        self.verbose_logger = verbose_logger

    def query(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables
            operation_name: Optional operation name for verbose logging

        Returns:
            Query response data

        Raises:
            LinearClientError: If the query fails
        """
        # Log query if verbose mode enabled
        self.verbose_logger.log_graphql_query(query, variables, operation_name)

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            start_time = time.perf_counter()

            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.API_URL, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                # Log response time
                duration_ms = (time.perf_counter() - start_time) * 1000
                self.verbose_logger.log_response_time(duration_ms)

                if "errors" in data:
                    errors = data["errors"]
                    error_messages = [e.get("message", str(e)) for e in errors]
                    raise LinearClientError(
                        f"GraphQL errors: {', '.join(error_messages)}"
                    )

                return data.get("data", {})

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise LinearClientError(
                    "Authentication failed. Check your API key.\n"
                    "Get your API key at: https://linear.app/settings/api"
                )
            elif e.response.status_code == 429:
                raise LinearClientError(
                    f"Rate limit exceeded. Linear API allows {self.RATE_LIMIT} requests per hour.\n"
                    "Please wait before making more requests."
                )
            else:
                raise LinearClientError(
                    f"HTTP error: {e.response.status_code} - {e.response.text}"
                )
        except httpx.RequestError as e:
            raise LinearClientError(f"Network error: {str(e)}")
