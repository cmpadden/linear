"""Base Linear API client for GraphQL interactions."""

import os
import time
from typing import Any, TYPE_CHECKING

import httpx

from linear.auth import AuthError, get_access_token

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
        self,
        api_key: str | None = None,
        verbose_logger: "VerboseLogger | None" = None,
        *,
        access_token: str | None = None,
    ) -> None:
        """Initialize the Linear client.

        Args:
            api_key: Explicit API key; otherwise use LINEAR_API_KEY, then saved OAuth.
            verbose_logger: Optional logger for verbose output.
            access_token: Explicit OAuth token for validating a new login. Cannot
                be combined with api_key; bypasses environment and saved credentials.

        Raises:
            LinearClientError: If credentials are missing or cannot be refreshed.
        """
        if api_key is not None and access_token is not None:
            raise LinearClientError("Provide either api_key or access_token, not both.")
        self.api_key = None if access_token else api_key or os.getenv("LINEAR_API_KEY")
        self._saved_oauth = not self.api_key and not access_token
        if self._saved_oauth:
            access_token = self._oauth_token()
        self.headers = {
            "Authorization": self.api_key or f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Store verbose logger (import here to avoid circular dependency)
        if verbose_logger is None:
            from linear.utils.context import VerboseLogger

            verbose_logger = VerboseLogger(enabled=False)
        self.verbose_logger = verbose_logger

    @staticmethod
    def _oauth_token() -> str:
        try:
            return get_access_token()
        except AuthError as exc:
            raise LinearClientError(str(exc)) from exc

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
        # Refresh before sending, including on long-lived client instances. Do not
        # blindly replay mutations on authentication errors.
        if self._saved_oauth:
            self.headers["Authorization"] = f"Bearer {self._oauth_token()}"

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
                    "Authentication failed. Check LINEAR_API_KEY if set, "
                    "or run `linear login` to renew your OAuth login."
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
