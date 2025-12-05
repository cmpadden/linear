"""Cycle-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING

from pydantic import ValidationError

from linear.models import Cycle, CycleConnection

if TYPE_CHECKING:
    from .client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_cycles(
    self: "LinearClient",
    team: str | None = None,
    active: bool = False,
    future: bool = False,
    past: bool = False,
    limit: int = 50,
    include_archived: bool = False,
) -> list[Cycle]:
    """List cycles with optional filters.

    Args:
        team: Filter by team name or key
        active: Show only active cycles
        future: Show only future cycles
        past: Show only past cycles
        limit: Maximum number of cycles to return (default: 50)
        include_archived: Include archived cycles (default: False)

    Returns:
        List of Cycle objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    query = """
    query Cycles($filter: CycleFilter, $first: Int, $includeArchived: Boolean) {
      cycles(filter: $filter, first: $first, includeArchived: $includeArchived) {
        nodes {
          id
          number
          name
          description
          startsAt
          endsAt
          completedAt
          archivedAt
          createdAt
          updatedAt
          isActive
          isFuture
          isPast
          isNext
          isPrevious
          progress
          team {
            id
            name
            key
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

    # Build filter object
    filters = {}

    # Team filter - needs to be at top level with 'or'
    if team:
        # Check if it's a UUID (simple check for hyphens)
        if "-" in team and len(team) == 36:
            # Treat as team ID
            filters["team"] = {"id": {"eq": team}}
        else:
            # Support both team key (exact match) and name (substring) with OR at top level
            filters["or"] = [
                {"team": {"key": {"eq": team.upper()}}},
                {"team": {"name": {"containsIgnoreCase": team}}},
            ]

    # Status filters
    if active:
        filters["isActive"] = {"eq": True}
    elif future:
        filters["isFuture"] = {"eq": True}
    elif past:
        filters["isPast"] = {"eq": True}

    variables = {
        "filter": filters if filters else None,
        "first": min(limit, 250),  # Linear API max
        "includeArchived": include_archived,
    }

    response = self.query(query, variables)

    try:
        connection = CycleConnection.model_validate(response.get("cycles", {}))
        return connection.nodes
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse cycles from API response: {e.errors()[0]['msg']}"
        )


def get_cycle(self: "LinearClient", cycle_id: str) -> Cycle:
    """Get a single cycle by ID.

    Args:
        cycle_id: Cycle ID (UUID)

    Returns:
        Cycle object

    Raises:
        LinearClientError: If the query fails, cycle not found, or data validation fails
    """
    query = """
    query Cycle($id: String!) {
      cycle(id: $id) {
        id
        number
        name
        description
        startsAt
        endsAt
        completedAt
        archivedAt
        createdAt
        updatedAt
        isActive
        isFuture
        isPast
        isNext
        isPrevious
        progress
        scopeHistory
        issueCountHistory
        completedScopeHistory
        team {
          id
          name
          key
        }
        issues(first: 100) {
          nodes {
            id
            identifier
            title
            state {
              name
              type
            }
            priority
            priorityLabel
            estimate
            assignee {
              name
            }
          }
        }
      }
    }
    """

    variables = {"id": cycle_id}

    response = self.query(query, variables)

    if not response.get("cycle"):
        raise LinearClientError(f"Cycle '{cycle_id}' not found")

    try:
        return Cycle.model_validate(response["cycle"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse cycle '{cycle_id}': {e.errors()[0]['msg']}"
        )
