"""Base Linear API client for GraphQL interactions."""

import os
from typing import Any

import httpx


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


class LinearClient:
    """Client for interacting with the Linear GraphQL API."""

    API_URL = "https://api.linear.app/graphql"
    RATE_LIMIT = 1500  # requests per hour

    def __init__(self, api_key: str | None = None):
        """Initialize the Linear client.

        Args:
            api_key: Linear API key. If not provided, will read from LINEAR_API_KEY env var.

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

    def query(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Query response data

        Raises:
            LinearClientError: If the query fails
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.API_URL, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()

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
