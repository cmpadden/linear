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


def create_project(
    self: "LinearClient",
    name: str,
    team_ids: list[str],
    description: str | None = None,
    lead_id: str | None = None,
    state: str | None = None,
    start_date: str | None = None,
    target_date: str | None = None,
    color: str | None = None,
    icon: str | None = None,
) -> Project:
    """Create a new project.

    Args:
        name: Project name (required)
        team_ids: List of team IDs (required, at least one)
        description: Project description
        lead_id: User ID of the project lead
        state: Project state (planned, started, paused, completed, canceled)
        start_date: Start date in ISO format (YYYY-MM-DD)
        target_date: Target date in ISO format (YYYY-MM-DD)
        color: Hex color code
        icon: Icon name

    Returns:
        Created Project object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation ProjectCreate($input: ProjectCreateInput!) {
      projectCreate(input: $input) {
        success
        project {
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
      }
    }
    """

    # Build input object
    input_data: dict[str, Any] = {
        "name": name,
        "teamIds": team_ids,
    }

    # Add optional fields if provided
    if description:
        input_data["description"] = description
    if lead_id:
        input_data["leadId"] = lead_id
    if state:
        input_data["state"] = state
    if start_date:
        input_data["startDate"] = start_date
    if target_date:
        input_data["targetDate"] = target_date
    if color:
        input_data["color"] = color
    if icon:
        input_data["icon"] = icon

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    project_create = response.get("projectCreate", {})
    if not project_create.get("success"):
        raise LinearClientError("Failed to create project")

    try:
        return Project.model_validate(project_create["project"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created project: {error_details['msg']} at {field_path}"
        )


def update_project(
    self: "LinearClient",
    project_id: str,
    name: str | None = None,
    description: str | None = None,
    team_ids: list[str] | None = None,
    lead_id: str | None = None,
    state: str | None = None,
    start_date: str | None = None,
    target_date: str | None = None,
    color: str | None = None,
    icon: str | None = None,
) -> Project:
    """Update an existing project.

    Args:
        project_id: Project ID (UUID) or slug
        name: New project name
        description: New project description
        team_ids: New list of team IDs (replaces all teams)
        lead_id: New project lead user ID
        state: New project state (planned, started, paused, completed, canceled)
        start_date: New start date in ISO format (YYYY-MM-DD)
        target_date: New target date in ISO format (YYYY-MM-DD)
        color: New hex color code
        icon: New icon name

    Returns:
        Updated Project object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation ProjectUpdate($id: String!, $input: ProjectUpdateInput!) {
      projectUpdate(id: $id, input: $input) {
        success
        project {
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
      }
    }
    """

    # Build input object - only include provided fields
    input_data: dict[str, Any] = {}

    if name is not None:
        input_data["name"] = name
    if description is not None:
        input_data["description"] = description
    if team_ids is not None:
        input_data["teamIds"] = team_ids
    if lead_id is not None:
        input_data["leadId"] = lead_id
    if state is not None:
        input_data["state"] = state
    if start_date is not None:
        input_data["startDate"] = start_date
    if target_date is not None:
        input_data["targetDate"] = target_date
    if color is not None:
        input_data["color"] = color
    if icon is not None:
        input_data["icon"] = icon

    variables = {
        "id": project_id,
        "input": input_data,
    }

    response = self.query(mutation, variables)

    # Check if mutation was successful
    project_update = response.get("projectUpdate", {})
    if not project_update.get("success"):
        raise LinearClientError("Failed to update project")

    try:
        return Project.model_validate(project_update["project"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse updated project: {error_details['msg']} at {field_path}"
        )


def delete_project(self: "LinearClient", project_id: str) -> bool:
    """Delete a project.

    Args:
        project_id: Project ID (UUID) or slug

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation ProjectDelete($id: String!) {
      projectDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": project_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    project_delete = response.get("projectDelete", {})
    if not project_delete.get("success"):
        raise LinearClientError("Failed to delete project")

    return True


def archive_project(self: "LinearClient", project_id: str) -> bool:
    """Archive a project.

    Args:
        project_id: Project ID (UUID) or slug

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation ProjectArchive($id: String!) {
      projectArchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": project_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    project_archive = response.get("projectArchive", {})
    if not project_archive.get("success"):
        raise LinearClientError("Failed to archive project")

    return True


def unarchive_project(self: "LinearClient", project_id: str) -> bool:
    """Unarchive a project.

    Args:
        project_id: Project ID (UUID) or slug

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation ProjectUnarchive($id: String!) {
      projectUnarchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": project_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    project_unarchive = response.get("projectUnarchive", {})
    if not project_unarchive.get("success"):
        raise LinearClientError("Failed to unarchive project")

    return True
