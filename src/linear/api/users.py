"""User-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import User, UserConnection

if TYPE_CHECKING:
    from .client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_users(
    self: "LinearClient",
    active_only: bool = True,
    limit: int = 50,
    include_disabled: bool = False,
) -> list[User]:
    """List users in the workspace.

    Args:
        active_only: Show only active users (default: True)
        limit: Maximum number of users to return (default: 50)
        include_disabled: Include disabled users (default: False)

    Returns:
        List of User objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    query = """
    query Users($filter: UserFilter, $first: Int, $includeDisabled: Boolean) {
      users(filter: $filter, first: $first, includeDisabled: $includeDisabled) {
        nodes {
          id
          name
          displayName
          email
          active
          admin
          createdAt
          updatedAt
          avatarUrl
          timezone
          organization {
            id
            name
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """

    # Build filter object
    filters = {}

    if active_only:
        filters["active"] = {"eq": True}

    variables = {
        "filter": filters if filters else None,
        "first": min(limit, 250),  # Linear API max
        "includeDisabled": include_disabled,
    }

    response = self.query(query, variables)

    try:
        connection = UserConnection.model_validate(response.get("users", {}))
        return connection.nodes
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse users from API response: {e.errors()[0]['msg']}"
        )


def get_user(self: "LinearClient", user_id: str) -> User:
    """Get a single user by ID or email.

    Args:
        user_id: User ID (UUID) or email

    Returns:
        User object

    Raises:
        LinearClientError: If the query fails, user not found, or data validation fails
    """
    query = """
    query User($id: String!) {
      user(id: $id) {
        id
        name
        displayName
        email
        active
        admin
        createdAt
        updatedAt
        avatarUrl
        timezone
        description
        statusEmoji
        statusLabel
        statusUntilAt
        organization {
          id
          name
          urlKey
        }
        teams {
          nodes {
            id
            name
            key
          }
        }
        assignedIssues(first: 10, filter: { state: { type: { in: ["started", "unstarted"] } } }) {
          nodes {
            id
            identifier
            title
            priority
            priorityLabel
            state {
              name
              type
            }
          }
        }
        createdIssues(first: 5) {
          nodes {
            id
            identifier
            title
          }
        }
      }
    }
    """

    variables = {"id": user_id}

    response = self.query(query, variables)

    if not response.get("user"):
        raise LinearClientError(f"User '{user_id}' not found")

    try:
        return User.model_validate(response["user"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse user '{user_id}': {e.errors()[0]['msg']}"
        )


def get_viewer(self: "LinearClient") -> dict[str, Any]:
    """Get the current authenticated user.

    Returns:
        Query response containing viewer (current user) data

    Raises:
        LinearClientError: If the query fails
    """
    query = """
    query {
      viewer {
        id
        name
        email
        teams {
          nodes {
            id
            key
            name
          }
        }
      }
    }
    """
    return self.query(query)
