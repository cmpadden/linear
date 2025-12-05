"""Label-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Label, LabelConnection

if TYPE_CHECKING:
    from .client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_labels(
    self: "LinearClient",
    limit: int = 50,
    team: str | None = None,
    include_archived: bool = False,
) -> list[Label]:
    """List issue labels.

    Args:
        limit: Maximum number of labels to return (default: 50)
        team: Filter by team ID or key
        include_archived: Include archived labels (default: False)

    Returns:
        List of Label objects

    Raises:
        LinearClientError: If the query fails or data validation fails

    Example:
        >>> client.list_labels(team="ENG", limit=20)
    """
    query = """
    query($first: Int, $filter: IssueLabelFilter, $includeArchived: Boolean) {
      issueLabels(first: $first, filter: $filter, includeArchived: $includeArchived) {
        nodes {
          id
          name
          description
          color
          createdAt
          updatedAt
          archivedAt
          team {
            id
            name
            key
          }
          parent {
            id
            name
          }
          children {
            nodes {
              id
            }
          }
          issues {
            nodes {
              id
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

    variables: dict[str, Any] = {
        "first": limit,
        "includeArchived": include_archived,
    }

    # Build filter
    filters: dict[str, Any] = {}

    # Handle team filter
    if team:
        # Check if it's a UUID (contains hyphens and is 36 chars)
        if "-" in team and len(team) == 36:
            filters["team"] = {"id": {"eq": team}}
        else:
            # Try to match by key or name
            filters["or"] = [
                {"team": {"key": {"eq": team.upper()}}},
                {"team": {"name": {"containsIgnoreCase": team}}},
            ]

    if filters:
        variables["filter"] = filters

    response = self.query(query, variables)

    try:
        connection = LabelConnection.model_validate(response.get("issueLabels", {}))
        return connection.nodes
    except ValidationError as e:
        import json

        raise LinearClientError(
            f"Failed to parse labels from API response:\n{json.dumps(e.errors(), indent=2)}"
        )
