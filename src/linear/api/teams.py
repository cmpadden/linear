"""Team-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Team, TeamConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_teams(
    self: "LinearClient",
    limit: int = 50,
    include_archived: bool = False,
    after: str | None = None,
    fetch_all: bool = False,
) -> tuple[list[Team], dict[str, Any]]:
    """List teams in the workspace.

    Args:
        limit: Maximum number of teams to return per page (default: 50)
        include_archived: Include archived teams (default: False)
        after: Cursor for pagination (fetches items after this cursor)
        fetch_all: If True, automatically fetch all pages (default: False)

    Returns:
        Tuple of (list of Team objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # GraphQL query
    query = """
    query Teams($filter: TeamFilter, $first: Int, $after: String, $includeArchived: Boolean) {
      teams(filter: $filter, first: $first, after: $after, includeArchived: $includeArchived) {
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

    # Fetch all pages if requested
    if fetch_all:
        all_teams: list[Team] = []
        current_cursor = after
        page_count = 0
        max_pages = 100  # Safety limit

        while page_count < max_pages:
            variables = {
                "filter": None,
                "first": min(limit, 250),  # Linear API max per page
                "after": current_cursor,
                "includeArchived": include_archived,
            }

            response = self.query(query, variables)

            try:
                connection = TeamConnection.model_validate(response.get("teams", {}))
                all_teams.extend(connection.nodes)
                page_count += 1

                if not connection.page_info.has_next_page:
                    break

                current_cursor = connection.page_info.end_cursor
            except ValidationError as e:
                raise LinearClientError(
                    f"Failed to parse teams from API response: {e.errors()[0]['msg']}"
                )

        pagination_info = {
            "hasNextPage": False,
            "endCursor": current_cursor or "",
            "totalFetched": len(all_teams),
        }
        return all_teams, pagination_info

    # Single page fetch
    variables = {
        "filter": None,
        "first": min(limit, 250),  # Linear API max
        "after": after,
        "includeArchived": include_archived,
    }

    response = self.query(query, variables)

    try:
        connection = TeamConnection.model_validate(response.get("teams", {}))
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
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


def get_team_states(self: "LinearClient", team_id: str) -> list[dict]:
    """Get workflow states for a team.

    Args:
        team_id: Team ID (UUID) or key (e.g., 'ENG')

    Returns:
        List of workflow state dictionaries with id, name, type, color

    Raises:
        LinearClientError: If the query fails or team not found
    """
    # GraphQL query
    query = """
    query Team($id: String!) {
      team(id: $id) {
        id
        states {
          nodes {
            id
            name
            type
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

    states_data = response.get("team", {}).get("states", {}).get("nodes", [])
    return states_data


def create_team(
    self: "LinearClient",
    name: str,
    key: str,
    description: str | None = None,
    private: bool = False,
) -> Team:
    """Create a new team.

    Args:
        name: Team name (required)
        key: Team key/identifier (required, e.g., 'ENG', 'DESIGN')
        description: Team description
        private: Whether team is private (default: False)

    Returns:
        Created Team object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation TeamCreate($input: TeamCreateInput!) {
      teamCreate(input: $input) {
        success
        team {
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
      }
    }
    """

    # Build input object
    input_data: dict[str, str | bool] = {
        "name": name,
        "key": key,
        "private": private,
    }

    # Add optional fields if provided
    if description:
        input_data["description"] = description

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    team_create = response.get("teamCreate", {})
    if not team_create.get("success"):
        raise LinearClientError("Failed to create team")

    try:
        return Team.model_validate(team_create["team"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created team: {error_details['msg']} at {field_path}"
        )


def update_team(
    self: "LinearClient",
    team_id: str,
    name: str | None = None,
    key: str | None = None,
    description: str | None = None,
    private: bool | None = None,
) -> Team:
    """Update an existing team.

    Args:
        team_id: Team ID (UUID) or key
        name: New team name
        key: New team key/identifier
        description: New team description
        private: Whether team is private

    Returns:
        Updated Team object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation TeamUpdate($id: String!, $input: TeamUpdateInput!) {
      teamUpdate(id: $id, input: $input) {
        success
        team {
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
      }
    }
    """

    # Build input object - only include provided fields
    input_data: dict[str, str | bool] = {}

    if name is not None:
        input_data["name"] = name
    if key is not None:
        input_data["key"] = key
    if description is not None:
        input_data["description"] = description
    if private is not None:
        input_data["private"] = private

    variables = {
        "id": team_id,
        "input": input_data,
    }

    response = self.query(mutation, variables)

    # Check if mutation was successful
    team_update = response.get("teamUpdate", {})
    if not team_update.get("success"):
        raise LinearClientError("Failed to update team")

    try:
        return Team.model_validate(team_update["team"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse updated team: {error_details['msg']} at {field_path}"
        )


def delete_team(self: "LinearClient", team_id: str) -> bool:
    """Delete a team.

    Args:
        team_id: Team ID (UUID) or key

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation TeamDelete($id: String!) {
      teamDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": team_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    team_delete = response.get("teamDelete", {})
    if not team_delete.get("success"):
        raise LinearClientError("Failed to delete team")

    return True


def archive_team(self: "LinearClient", team_id: str) -> bool:
    """Archive a team.

    Args:
        team_id: Team ID (UUID) or key

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation TeamArchive($id: String!) {
      teamArchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": team_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    team_archive = response.get("teamArchive", {})
    if not team_archive.get("success"):
        raise LinearClientError("Failed to archive team")

    return True
