"""Cycle-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Cycle, CycleConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


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
    after: str | None = None,
    fetch_all: bool = False,
) -> tuple[list[Cycle], dict[str, Any]]:
    """List cycles with optional filters.

    Args:
        team: Filter by team name or key
        active: Show only active cycles
        future: Show only future cycles
        past: Show only past cycles
        limit: Maximum number of cycles to return per page (default: 50)
        include_archived: Include archived cycles (default: False)
        after: Cursor for pagination (fetches items after this cursor)
        fetch_all: If True, automatically fetch all pages (default: False)

    Returns:
        Tuple of (list of Cycle objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    query = """
    query Cycles($filter: CycleFilter, $first: Int, $after: String, $includeArchived: Boolean) {
      cycles(filter: $filter, first: $first, after: $after, includeArchived: $includeArchived) {
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

    # Fetch all pages if requested
    if fetch_all:
        all_cycles: list[Cycle] = []
        current_cursor = after
        page_count = 0
        max_pages = 100

        while page_count < max_pages:
            variables = {
                "filter": filters if filters else None,
                "first": min(limit, 250),
                "after": current_cursor,
                "includeArchived": include_archived,
            }

            response = self.query(query, variables)

            try:
                connection = CycleConnection.model_validate(response.get("cycles", {}))
                all_cycles.extend(connection.nodes)
                page_count += 1

                if not connection.page_info.has_next_page:
                    break

                current_cursor = connection.page_info.end_cursor
            except ValidationError as e:
                raise LinearClientError(
                    f"Failed to parse cycles from API response: {e.errors()[0]['msg']}"
                )

        pagination_info = {
            "hasNextPage": False,
            "endCursor": current_cursor or "",
            "totalFetched": len(all_cycles),
        }
        return all_cycles, pagination_info

    # Single page fetch
    variables = {
        "filter": filters if filters else None,
        "first": min(limit, 250),
        "after": after,
        "includeArchived": include_archived,
    }

    response = self.query(query, variables)

    try:
        connection = CycleConnection.model_validate(response.get("cycles", {}))
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
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


def create_cycle(
    self: "LinearClient",
    name: str,
    team_id: str,
    starts_at: str,
    ends_at: str,
    description: str | None = None,
) -> Cycle:
    """Create a new cycle.

    Args:
        name: Cycle name (required)
        team_id: Team UUID (required)
        starts_at: Start date in ISO format (YYYY-MM-DD or ISO 8601)
        ends_at: End date in ISO format (YYYY-MM-DD or ISO 8601)
        description: Cycle description

    Returns:
        Created Cycle object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation CycleCreate($input: CycleCreateInput!) {
      cycleCreate(input: $input) {
        success
        cycle {
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
        }
      }
    }
    """

    # Build input object
    input_data: dict[str, str] = {
        "name": name,
        "teamId": team_id,
        "startsAt": starts_at,
        "endsAt": ends_at,
    }

    # Add optional fields if provided
    if description:
        input_data["description"] = description

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    cycle_create = response.get("cycleCreate", {})
    if not cycle_create.get("success"):
        raise LinearClientError("Failed to create cycle")

    try:
        return Cycle.model_validate(cycle_create["cycle"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created cycle: {error_details['msg']} at {field_path}"
        )


def update_cycle(
    self: "LinearClient",
    cycle_id: str,
    name: str | None = None,
    starts_at: str | None = None,
    ends_at: str | None = None,
    description: str | None = None,
) -> Cycle:
    """Update an existing cycle.

    Args:
        cycle_id: Cycle UUID
        name: New cycle name
        starts_at: New start date in ISO format (YYYY-MM-DD or ISO 8601)
        ends_at: New end date in ISO format (YYYY-MM-DD or ISO 8601)
        description: New cycle description

    Returns:
        Updated Cycle object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation CycleUpdate($id: String!, $input: CycleUpdateInput!) {
      cycleUpdate(id: $id, input: $input) {
        success
        cycle {
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
        }
      }
    }
    """

    # Build input object - only include provided fields
    input_data: dict[str, str] = {}

    if name is not None:
        input_data["name"] = name
    if starts_at is not None:
        input_data["startsAt"] = starts_at
    if ends_at is not None:
        input_data["endsAt"] = ends_at
    if description is not None:
        input_data["description"] = description

    variables = {
        "id": cycle_id,
        "input": input_data,
    }

    response = self.query(mutation, variables)

    # Check if mutation was successful
    cycle_update = response.get("cycleUpdate", {})
    if not cycle_update.get("success"):
        raise LinearClientError("Failed to update cycle")

    try:
        return Cycle.model_validate(cycle_update["cycle"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse updated cycle: {error_details['msg']} at {field_path}"
        )


def delete_cycle(self: "LinearClient", cycle_id: str) -> bool:
    """Delete a cycle.

    Args:
        cycle_id: Cycle UUID

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation CycleDelete($id: String!) {
      cycleDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": cycle_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    cycle_delete = response.get("cycleDelete", {})
    if not cycle_delete.get("success"):
        raise LinearClientError("Failed to delete cycle")

    return True


def archive_cycle(self: "LinearClient", cycle_id: str) -> bool:
    """Archive a cycle.

    Args:
        cycle_id: Cycle UUID

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation CycleArchive($id: String!) {
      cycleArchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": cycle_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    cycle_archive = response.get("cycleArchive", {})
    if not cycle_archive.get("success"):
        raise LinearClientError("Failed to archive cycle")

    return True
