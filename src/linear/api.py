"""Linear API client for GraphQL interactions."""

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

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
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
                    raise LinearClientError(f"GraphQL errors: {', '.join(error_messages)}")

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
                raise LinearClientError(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise LinearClientError(f"Network error: {str(e)}")

    def list_issues(
        self,
        assignee: str | None = None,
        project: str | None = None,
        status: str | None = None,
        team: str | None = None,
        priority: int | None = None,
        labels: list[str] | None = None,
        limit: int = 50,
        include_archived: bool = False,
        sort: str = "updated",
    ) -> dict[str, Any]:
        """List issues with optional filters.

        Args:
            assignee: Filter by assignee email
            project: Filter by project name
            status: Filter by issue status/state
            team: Filter by team name or key
            priority: Filter by priority (0-4)
            labels: Filter by label names
            limit: Maximum number of issues to return (default: 50)
            include_archived: Include archived issues (default: False)
            sort: Sort field: created, updated, priority (default: updated)

        Returns:
            Query response containing issues

        Raises:
            LinearClientError: If the query fails
        """
        # Build filter object
        filters = {}

        if assignee:
            filters["assignee"] = {"email": {"eq": assignee}}

        if project:
            # Support both UUID and name matching
            if len(project) == 36 and "-" in project:  # Simple UUID check
                filters["project"] = {"id": {"eq": project}}
            else:
                filters["project"] = {"name": {"contains": project}}

        if status:
            filters["state"] = {"name": {"eqIgnoreCase": status}}

        if team:
            # Support both team key and name
            filters["team"] = {
                "or": [{"key": {"eqIgnoreCase": team}}, {"name": {"containsIgnoreCase": team}}]
            }

        if priority is not None:
            filters["priority"] = {"eq": priority}

        if labels:
            filters["labels"] = {"name": {"in": labels}}

        # Determine order by
        order_by_map = {"created": "createdAt", "updated": "updatedAt", "priority": "priority"}
        order_by = order_by_map.get(sort, "updatedAt")

        # GraphQL query
        query = """
        query Issues($filter: IssueFilter, $first: Int, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
          issues(filter: $filter, first: $first, includeArchived: $includeArchived, orderBy: $orderBy) {
            nodes {
              id
              identifier
              title
              description
              priority
              priorityLabel
              url
              createdAt
              updatedAt
              completedAt
              state {
                name
                type
              }
              assignee {
                name
                email
              }
              project {
                name
              }
              team {
                name
                key
              }
              labels {
                nodes {
                  name
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """

        variables = {
            "filter": filters if filters else None,
            "first": min(limit, 250),  # Linear API max
            "includeArchived": include_archived,
            "orderBy": order_by,
        }

        return self.query(query, variables)

    def list_projects(
        self,
        state: str | None = None,
        team: str | None = None,
        limit: int = 50,
        include_archived: bool = False,
        sort: str = "updated",
    ) -> dict[str, Any]:
        """List projects with optional filters.

        Args:
            state: Filter by project state (planned, started, paused, completed, canceled)
            team: Filter by team name or key
            limit: Maximum number of projects to return (default: 50)
            include_archived: Include archived projects (default: False)
            sort: Sort field: created, updated (default: updated)

        Returns:
            Query response containing projects

        Raises:
            LinearClientError: If the query fails
        """
        # Build filter object
        filters = {}

        if state:
            filters["state"] = {"eqIgnoreCase": state}

        if team:
            # Support both team key and name
            filters["or"] = [
                {"teams": {"some": {"key": {"eqIgnoreCase": team}}}},
                {"teams": {"some": {"name": {"containsIgnoreCase": team}}}},
            ]

        # Determine order by
        order_by_map = {"created": "createdAt", "updated": "updatedAt"}
        order_by = order_by_map.get(sort, "updatedAt")

        # GraphQL query
        query = """
        query Projects($filter: ProjectFilter, $first: Int, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
          projects(filter: $filter, first: $first, includeArchived: $includeArchived, orderBy: $orderBy) {
            nodes {
              id
              name
              description
              state
              progress
              startDate
              targetDate
              url
              createdAt
              updatedAt
              archivedAt
              color
              icon
              lead {
                name
                email
              }
              teams {
                nodes {
                  name
                  key
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """

        variables = {
            "filter": filters if filters else None,
            "first": min(limit, 250),  # Linear API max
            "includeArchived": include_archived,
            "orderBy": order_by,
        }

        return self.query(query, variables)
