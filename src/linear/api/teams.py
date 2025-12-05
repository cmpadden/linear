"""Team-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING

from pydantic import ValidationError

from linear.models import Team, TeamConnection

if TYPE_CHECKING:
    from .client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_teams(
    self: "LinearClient",
    limit: int = 50,
    include_archived: bool = False,
) -> list[Team]:
    """List teams in the workspace.

    Args:
        limit: Maximum number of teams to return (default: 50)
        include_archived: Include archived teams (default: False)

    Returns:
        List of Team objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # GraphQL query
    query = """
    query Teams($filter: TeamFilter, $first: Int, $includeArchived: Boolean) {
      teams(filter: $filter, first: $first, includeArchived: $includeArchived) {
        nodes {
          id
          name
          key
          description
          color
          icon
          private
          archivedAt
          createdAt
          updatedAt
          cyclesEnabled
          members {
            nodes {
              id
              name
            }
          }
          issues {
            nodes {
              id
            }
          }
          projects {
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

    variables = {
        "filter": None,
        "first": min(limit, 250),  # Linear API max
        "includeArchived": include_archived,
    }

    response = self.query(query, variables)

    try:
        connection = TeamConnection.model_validate(response.get("teams", {}))
        return connection.nodes
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse teams from API response: {e.errors()[0]['msg']}"
        )


def get_team(self: "LinearClient", team_id: str) -> Team:
    """Get a single team by ID or key.

    Args:
        team_id: Team ID (UUID) or key (e.g., 'ENG')

    Returns:
        Team object

    Raises:
        LinearClientError: If the query fails, team not found, or data validation fails
    """
    # GraphQL query
    query = """
    query Team($id: String!) {
      team(id: $id) {
        id
        name
        key
        description
        color
        icon
        private
        archivedAt
        createdAt
        updatedAt
        cyclesEnabled
        timezone
        organization {
          id
          name
        }
        members {
          nodes {
            id
            name
            email
            displayName
            active
            admin
            avatarUrl
          }
        }
        issues(first: 50, filter: { state: { type: { in: ["started", "unstarted"] } } }) {
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
            assignee {
              name
            }
          }
        }
        projects(first: 20) {
          nodes {
            id
            name
            state
            progress
            lead {
              name
            }
          }
        }
        states {
          nodes {
            id
            name
            type
            color
          }
        }
        labels {
          nodes {
            id
            name
            color
          }
        }
      }
    }
    """

    variables = {"id": team_id}

    response = self.query(query, variables)

    if not response.get("team"):
        raise LinearClientError(f"Team '{team_id}' not found")

    try:
        return Team.model_validate(response["team"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse team '{team_id}': {e.errors()[0]['msg']}"
        )
