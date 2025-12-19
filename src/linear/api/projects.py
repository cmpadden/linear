"""Project-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Project, ProjectConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_projects(
    self: "LinearClient",
    state: str | None = None,
    team: str | None = None,
    limit: int = 50,
    include_archived: bool = False,
    sort: str = "updated",
    after: str | None = None,
    fetch_all: bool = False,
) -> tuple[list[Project], dict[str, Any]]:
    """List projects with optional filters.

    Args:
        state: Filter by project state (planned, started, paused, completed, canceled)
        team: Filter by team name or key
        limit: Maximum number of projects to return per page (default: 50)
        include_archived: Include archived projects (default: False)
        sort: Sort field: created, updated (default: updated)
        after: Cursor for pagination (fetches items after this cursor)
        fetch_all: If True, automatically fetch all pages (default: False)

    Returns:
        Tuple of (list of Project objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
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
    query Projects($filter: ProjectFilter, $first: Int, $after: String, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
      projects(filter: $filter, first: $first, after: $after, includeArchived: $includeArchived, orderBy: $orderBy) {
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

    # Fetch all pages if requested
    if fetch_all:
        all_projects: list[Project] = []
        current_cursor = after
        page_count = 0
        max_pages = 100  # Safety limit to prevent infinite loops

        while page_count < max_pages:
            variables = {
                "filter": filters if filters else None,
                "first": min(limit, 250),  # Linear API max per page
                "after": current_cursor,
                "includeArchived": include_archived,
                "orderBy": order_by,
            }

            response = self.query(query, variables)

            try:
                connection = ProjectConnection.model_validate(
                    response.get("projects", {})
                )
                all_projects.extend(connection.nodes)
                page_count += 1

                if not connection.page_info.has_next_page:
                    break

                current_cursor = connection.page_info.end_cursor
            except ValidationError as e:
                import json

                raise LinearClientError(
                    f"Failed to parse projects from API response:\n{json.dumps(e.errors(), indent=2)}"
                )

        pagination_info = {
            "hasNextPage": False,
            "endCursor": current_cursor or "",
            "totalFetched": len(all_projects),
        }
        return all_projects, pagination_info

    # Single page fetch
    variables = {
        "filter": filters if filters else None,
        "first": min(limit, 250),  # Linear API max
        "after": after,
        "includeArchived": include_archived,
        "orderBy": order_by,
    }

    response = self.query(query, variables)

    try:
        connection = ProjectConnection.model_validate(response.get("projects", {}))
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
    except ValidationError as e:
        import json

        raise LinearClientError(
            f"Failed to parse projects from API response:\n{json.dumps(e.errors(), indent=2)}"
        )


def get_project(self: "LinearClient", project_id: str) -> Project:
    """Get a single project by ID or slug.

    Args:
        project_id: Project ID (UUID) or slug

    Returns:
        Project object

    Raises:
        LinearClientError: If the query fails, project not found, or data validation fails
    """
    # GraphQL query
    query = """
    query Project($id: String!) {
      project(id: $id) {
        id
        name
        description
        state
        progress
        startDate
        targetDate
        completedAt
        canceledAt
        url
        createdAt
        updatedAt
        archivedAt
        color
        icon
        slugId
        lead {
          name
          email
          avatarUrl
        }
        creator {
          name
          email
        }
        teams {
          nodes {
            name
            key
          }
        }
        members {
          nodes {
            name
            email
          }
        }
        issues(first: 50) {
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
      }
    }
    """

    variables = {"id": project_id}

    response = self.query(query, variables)

    if not response.get("project"):
        raise LinearClientError(f"Project '{project_id}' not found")

    try:
        return Project.model_validate(response["project"])
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse project '{project_id}': {e.errors()[0]['msg']}"
        )
