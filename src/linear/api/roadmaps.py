"""Roadmap-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Roadmap, RoadmapConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_roadmaps(
    self: "LinearClient",
    limit: int = 50,
    include_archived: bool = False,
    sort: str = "updated",
    after: str | None = None,
    fetch_all: bool = False,
) -> tuple[list[Roadmap], dict[str, Any]]:
    """List roadmaps with optional filters.

    Args:
        limit: Maximum number of roadmaps to return per page (default: 50)
        include_archived: Include archived roadmaps (default: False)
        sort: Sort field: created, updated (default: updated)
        after: Cursor for pagination (fetches items after this cursor)
        fetch_all: If True, automatically fetch all pages (default: False)

    Returns:
        Tuple of (list of Roadmap objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # Determine order by
    order_by_map = {"created": "createdAt", "updated": "updatedAt"}
    order_by = order_by_map.get(sort, "updatedAt")

    # GraphQL query
    query = """
    query Roadmaps($first: Int, $after: String, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
      roadmaps(first: $first, after: $after, includeArchived: $includeArchived, orderBy: $orderBy) {
        nodes {
          id
          name
          description
          slugId
          url
          createdAt
          updatedAt
          archivedAt
          creator {
            name
            email
          }
          owner {
            name
            email
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
        all_roadmaps: list[Roadmap] = []
        current_cursor = after
        page_count = 0
        max_pages = 100  # Safety limit to prevent infinite loops

        while page_count < max_pages:
            variables = {
                "first": min(limit, 250),  # Linear API max per page
                "after": current_cursor,
                "includeArchived": include_archived,
                "orderBy": order_by,
            }

            response = self.query(query, variables)

            try:
                connection = RoadmapConnection.model_validate(
                    response.get("roadmaps", {})
                )
                all_roadmaps.extend(connection.nodes)
                page_count += 1

                if not connection.page_info.has_next_page:
                    break

                current_cursor = connection.page_info.end_cursor
            except ValidationError as e:
                import json

                raise LinearClientError(
                    f"Failed to parse roadmaps from API response:\n{json.dumps(e.errors(), indent=2)}"
                )

        pagination_info = {
            "hasNextPage": False,
            "endCursor": current_cursor or "",
            "totalFetched": len(all_roadmaps),
        }
        return all_roadmaps, pagination_info

    # Single page fetch
    variables = {
        "first": min(limit, 250),  # Linear API max
        "after": after,
        "includeArchived": include_archived,
        "orderBy": order_by,
    }

    response = self.query(query, variables)

    try:
        connection = RoadmapConnection.model_validate(response.get("roadmaps", {}))
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
    except ValidationError as e:
        import json

        raise LinearClientError(
            f"Failed to parse roadmaps from API response:\n{json.dumps(e.errors(), indent=2)}"
        )


def get_roadmap(self: "LinearClient", roadmap_id: str) -> Roadmap:
    """Get a single roadmap by ID or slug.

    Args:
        roadmap_id: Roadmap ID (UUID) or slug

    Returns:
        Roadmap object

    Raises:
        LinearClientError: If the query fails, roadmap not found, or data validation fails
    """
    # GraphQL query
    query = """
    query Roadmap($id: String!) {
      roadmap(id: $id) {
        id
        name
        description
        slugId
        url
        createdAt
        updatedAt
        archivedAt
        creator {
          name
          email
          avatarUrl
        }
        owner {
          name
          email
          avatarUrl
        }
        projects {
          nodes {
            id
            name
            state
            progress
            targetDate
          }
        }
      }
    }
    """

    variables = {"id": roadmap_id}

    response = self.query(query, variables)

    if not response.get("roadmap"):
        raise LinearClientError(f"Roadmap '{roadmap_id}' not found")

    try:
        return Roadmap.model_validate(response["roadmap"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse roadmap '{roadmap_id}': {e.errors()[0]['msg']}"
        )


def create_roadmap(
    self: "LinearClient",
    name: str,
    description: str | None = None,
    owner_id: str | None = None,
) -> Roadmap:
    """Create a new roadmap.

    Args:
        name: Name of the roadmap
        description: Optional description
        owner_id: Optional owner user ID

    Returns:
        Created Roadmap object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation RoadmapCreate($input: RoadmapCreateInput!) {
      roadmapCreate(input: $input) {
        success
        roadmap {
          id
          name
          description
          slugId
          url
          createdAt
          updatedAt
          creator {
            name
            email
          }
          owner {
            name
            email
          }
        }
      }
    }
    """

    input_data: dict[str, Any] = {"name": name}
    if description:
        input_data["description"] = description
    if owner_id:
        input_data["ownerId"] = owner_id

    variables = {"input": input_data}

    response = self.query(mutation, variables)

    result = response.get("roadmapCreate", {})
    if not result.get("success"):
        raise LinearClientError("Failed to create roadmap")

    try:
        return Roadmap.model_validate(result["roadmap"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse created roadmap: {e.errors()[0]['msg']}"
        )


def update_roadmap(
    self: "LinearClient",
    roadmap_id: str,
    name: str | None = None,
    description: str | None = None,
    owner_id: str | None = None,
) -> Roadmap:
    """Update an existing roadmap.

    Args:
        roadmap_id: Roadmap ID to update
        name: Optional new name
        description: Optional new description
        owner_id: Optional new owner user ID

    Returns:
        Updated Roadmap object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation RoadmapUpdate($id: String!, $input: RoadmapUpdateInput!) {
      roadmapUpdate(id: $id, input: $input) {
        success
        roadmap {
          id
          name
          description
          slugId
          url
          createdAt
          updatedAt
          archivedAt
          creator {
            name
            email
          }
          owner {
            name
            email
          }
        }
      }
    }
    """

    input_data: dict[str, Any] = {}
    if name is not None:
        input_data["name"] = name
    if description is not None:
        input_data["description"] = description
    if owner_id is not None:
        input_data["ownerId"] = owner_id

    if not input_data:
        raise LinearClientError("At least one field must be provided to update")

    variables = {"id": roadmap_id, "input": input_data}

    response = self.query(mutation, variables)

    result = response.get("roadmapUpdate", {})
    if not result.get("success"):
        raise LinearClientError(f"Failed to update roadmap '{roadmap_id}'")

    try:
        return Roadmap.model_validate(result["roadmap"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse updated roadmap: {e.errors()[0]['msg']}"
        )
