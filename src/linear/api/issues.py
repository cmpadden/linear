"""Issue-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Issue, IssueConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def _to_iso_datetime(date_str: str, start_of_day: bool = True) -> str:
    """Convert YYYY-MM-DD to ISO 8601 datetime.

    Args:
        date_str: Date in YYYY-MM-DD format
        start_of_day: If True, use 00:00:00; if False, use 23:59:59

    Returns:
        ISO 8601 datetime string (e.g., "2025-01-01T00:00:00Z")

    Raises:
        LinearClientError: If date format is invalid
    """
    from datetime import datetime

    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        raise LinearClientError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

    if start_of_day:
        return f"{date.date()}T00:00:00Z"
    else:
        return f"{date.date()}T23:59:59Z"


def list_issues(
    self: "LinearClient",
    assignee: str | None = None,
    unassigned_only: bool = False,
    creator: str | None = None,
    project: str | None = None,
    status: str | None = None,
    team: str | None = None,
    priority: int | None = None,
    labels: list[str] | None = None,
    # Date range filters
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    updated_before: str | None = None,
    # Query string filter
    filter_query: str | None = None,
    # Pagination and sorting
    limit: int = 50,
    include_archived: bool = False,
    sort: str = "updated",
    after: str | None = None,
    fetch_all: bool = False,
) -> tuple[list[Issue], dict[str, Any]]:
    """List issues with optional filters.

    Args:
        assignee: Filter by assignee email
        unassigned_only: Filter to issues with no assignee
        creator: Filter by issue creator email
        project: Filter by project name
        status: Filter by issue status/state
        team: Filter by team key (e.g., ENG, DESIGN)
        priority: Filter by priority (0-4)
        labels: Filter by label names
        created_after: Filter issues created after date (YYYY-MM-DD)
        created_before: Filter issues created before date (YYYY-MM-DD)
        updated_after: Filter issues updated after date (YYYY-MM-DD)
        updated_before: Filter issues updated before date (YYYY-MM-DD)
        filter_query: Query string for complex filters (e.g., "team:ENG OR team:DESIGN AND priority:1")
        limit: Maximum number of issues to return per page (default: 50)
        include_archived: Include archived issues (default: False)
        sort: Sort field: created, updated, priority (default: updated)
        after: Cursor for pagination (fetches items after this cursor)
        fetch_all: If True, automatically fetch all pages (default: False)

    Returns:
        Tuple of (list of Issue objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # Build filter object
    filters = {}

    # If filter_query is provided, parse it and use as the base filter
    if filter_query:
        from linear.query_parser import parse_query, QueryParseError

        try:
            filters = parse_query(filter_query)
        except QueryParseError as e:
            raise LinearClientError(f"Invalid filter query: {e}")

    # If simple filters are provided, add them (they AND with filter_query if both exist)
    simple_filters = {}

    if assignee:
        simple_filters["assignee"] = {"email": {"eq": assignee}}
    elif unassigned_only:
        simple_filters["assignee"] = {"null": True}

    if creator:
        simple_filters["creator"] = {"email": {"eq": creator}}

    if project:
        # Support both UUID and name matching
        if len(project) == 36 and "-" in project:  # Simple UUID check
            simple_filters["project"] = {"id": {"eq": project}}
        else:
            simple_filters["project"] = {"name": {"contains": project}}

    if status:
        simple_filters["state"] = {"name": {"eqIgnoreCase": status}}

    if team:
        # Filter by team key only (keys are unique identifiers)
        simple_filters["team"] = {"key": {"eqIgnoreCase": team}}

    if priority is not None:
        simple_filters["priority"] = {"eq": priority}

    if labels:
        simple_filters["labels"] = {"name": {"in": labels}}

    # Date range filters
    if created_after:
        simple_filters["createdAt"] = simple_filters.get("createdAt", {})
        simple_filters["createdAt"]["gte"] = _to_iso_datetime(
            created_after, start_of_day=True
        )

    if created_before:
        simple_filters["createdAt"] = simple_filters.get("createdAt", {})
        simple_filters["createdAt"]["lt"] = _to_iso_datetime(
            created_before, start_of_day=False
        )

    if updated_after:
        simple_filters["updatedAt"] = simple_filters.get("updatedAt", {})
        simple_filters["updatedAt"]["gte"] = _to_iso_datetime(
            updated_after, start_of_day=True
        )

    if updated_before:
        simple_filters["updatedAt"] = simple_filters.get("updatedAt", {})
        simple_filters["updatedAt"]["lt"] = _to_iso_datetime(
            updated_before, start_of_day=False
        )

    # Combine filter_query with simple filters if both exist
    if filters and simple_filters:
        filters = {"and": [filters, simple_filters]}
    elif simple_filters:
        filters = simple_filters

    # Determine order by
    order_by_map = {
        "created": "createdAt",
        "updated": "updatedAt",
        "priority": "priority",
    }
    order_by = order_by_map.get(sort, "updatedAt")

    # GraphQL query
    query = """
    query Issues($filter: IssueFilter, $first: Int, $after: String, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
      issues(filter: $filter, first: $first, after: $after, includeArchived: $includeArchived, orderBy: $orderBy) {
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
            id
            name
            type
            color
          }
          assignee {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
          creator {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
          project {
            id
            name
            state
            progress
            url
            createdAt
            updatedAt
          }
          team {
            id
            name
            key
            createdAt
            updatedAt
            cyclesEnabled
            private
          }
          cycle {
            id
            name
            number
            startsAt
            endsAt
            progress
            isActive
            isFuture
            isPast
            isNext
            isPrevious
            createdAt
            updatedAt
            team {
              id
              name
              key
              createdAt
              updatedAt
              cyclesEnabled
              private
            }
          }
          labels {
            nodes {
              id
              name
              color
              createdAt
              updatedAt
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
        all_issues: list[Issue] = []
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
                connection = IssueConnection.model_validate(response.get("issues", {}))
                all_issues.extend(connection.nodes)
                page_count += 1

                if not connection.page_info.has_next_page:
                    break

                current_cursor = connection.page_info.end_cursor
            except ValidationError as e:
                error_details = e.errors()[0]
                field_path = " -> ".join(str(loc) for loc in error_details["loc"])
                raise LinearClientError(
                    f"Failed to parse issues from API response: {error_details['msg']} at {field_path}"
                )

        pagination_info = {
            "hasNextPage": False,
            "endCursor": current_cursor or "",
            "totalFetched": len(all_issues),
        }
        return all_issues, pagination_info

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
        connection = IssueConnection.model_validate(response.get("issues", {}))
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse issues from API response: {error_details['msg']} at {field_path}"
        )


def search_issues(
    self: "LinearClient",
    query: str,
    # Additional filters (same as list_issues)
    assignee: str | None = None,
    creator: str | None = None,
    project: str | None = None,
    status: str | None = None,
    team: str | None = None,
    priority: int | None = None,
    labels: list[str] | None = None,
    # Date range filters
    created_after: str | None = None,
    created_before: str | None = None,
    updated_after: str | None = None,
    updated_before: str | None = None,
    # Query string filter
    filter_query: str | None = None,
    # Pagination and sorting
    limit: int = 50,
    include_archived: bool = False,
    sort: str = "updated",
    after: str | None = None,
    fetch_all: bool = False,
) -> tuple[list[Issue], dict[str, Any]]:
    """Search issues by title and description with optional additional filters.

    Args:
        query: Search query (searches issue titles and descriptions, case-insensitive)
        assignee: Filter by assignee email
        creator: Filter by issue creator email
        project: Filter by project name
        status: Filter by issue status/state
        team: Filter by team key (e.g., ENG, DESIGN)
        priority: Filter by priority (0-4)
        labels: Filter by label names
        created_after: Filter issues created after date (YYYY-MM-DD)
        created_before: Filter issues created before date (YYYY-MM-DD)
        updated_after: Filter issues updated after date (YYYY-MM-DD)
        updated_before: Filter issues updated before date (YYYY-MM-DD)
        filter_query: Query string for complex filters (e.g., "team:ENG OR team:DESIGN AND priority:1")
        limit: Maximum number of issues to return per page (default: 50)
        include_archived: Include archived issues (default: False)
        sort: Sort field: created, updated, priority (default: updated)
        after: Cursor for pagination (fetches items after this cursor)
        fetch_all: If True, automatically fetch all pages (default: False)

    Returns:
        Tuple of (list of matching Issue objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # Build base search filter (title OR description)
    search_filter = {
        "or": [
            {"title": {"containsIgnoreCase": query}},
            {"description": {"containsIgnoreCase": query}},
        ]
    }

    # If filter_query is provided, parse it
    query_filter = {}
    if filter_query:
        from linear.query_parser import parse_query, QueryParseError

        try:
            query_filter = parse_query(filter_query)
        except QueryParseError as e:
            raise LinearClientError(f"Invalid filter query: {e}")

    # Build simple filters
    simple_filters = {}

    if assignee:
        simple_filters["assignee"] = {"email": {"eq": assignee}}

    if creator:
        simple_filters["creator"] = {"email": {"eq": creator}}

    if project:
        if len(project) == 36 and "-" in project:
            simple_filters["project"] = {"id": {"eq": project}}
        else:
            simple_filters["project"] = {"name": {"contains": project}}

    if status:
        simple_filters["state"] = {"name": {"eqIgnoreCase": status}}

    if team:
        simple_filters["team"] = {"key": {"eqIgnoreCase": team}}

    if priority is not None:
        simple_filters["priority"] = {"eq": priority}

    if labels:
        simple_filters["labels"] = {"name": {"in": labels}}

    # Date range filters
    if created_after:
        simple_filters["createdAt"] = simple_filters.get("createdAt", {})
        simple_filters["createdAt"]["gte"] = _to_iso_datetime(
            created_after, start_of_day=True
        )

    if created_before:
        simple_filters["createdAt"] = simple_filters.get("createdAt", {})
        simple_filters["createdAt"]["lt"] = _to_iso_datetime(
            created_before, start_of_day=False
        )

    if updated_after:
        simple_filters["updatedAt"] = simple_filters.get("updatedAt", {})
        simple_filters["updatedAt"]["gte"] = _to_iso_datetime(
            updated_after, start_of_day=True
        )

    if updated_before:
        simple_filters["updatedAt"] = simple_filters.get("updatedAt", {})
        simple_filters["updatedAt"]["lt"] = _to_iso_datetime(
            updated_before, start_of_day=False
        )

    # Combine all filters with AND logic
    all_filters = [search_filter]
    if query_filter:
        all_filters.append(query_filter)
    if simple_filters:
        all_filters.append(simple_filters)

    if len(all_filters) == 1:
        filters = all_filters[0]
    else:
        filters = {"and": all_filters}

    # Determine order by
    order_by_map = {
        "created": "createdAt",
        "updated": "updatedAt",
        "priority": "priority",
    }
    order_by = order_by_map.get(sort, "updatedAt")

    # GraphQL query (same as list_issues)
    query_str = """
    query Issues($filter: IssueFilter, $first: Int, $after: String, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
      issues(filter: $filter, first: $first, after: $after, includeArchived: $includeArchived, orderBy: $orderBy) {
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
            id
            name
            type
            color
          }
          assignee {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
          creator {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
          project {
            id
            name
            state
            progress
            url
            createdAt
            updatedAt
          }
          team {
            id
            name
            key
            createdAt
            updatedAt
            cyclesEnabled
            private
          }
          cycle {
            id
            name
            number
            startsAt
            endsAt
            progress
            isActive
            isFuture
            isPast
            isNext
            isPrevious
            createdAt
            updatedAt
            team {
              id
              name
              key
              createdAt
              updatedAt
              cyclesEnabled
              private
            }
          }
          labels {
            nodes {
              id
              name
              color
              createdAt
              updatedAt
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
        all_issues: list[Issue] = []
        current_cursor = after
        page_count = 0
        max_pages = 100  # Safety limit

        while page_count < max_pages:
            variables = {
                "filter": filters,
                "first": min(limit, 250),  # Linear API max per page
                "after": current_cursor,
                "includeArchived": include_archived,
                "orderBy": order_by,
            }

            response = self.query(query_str, variables)

            try:
                connection = IssueConnection.model_validate(response.get("issues", {}))
                all_issues.extend(connection.nodes)
                page_count += 1

                if not connection.page_info.has_next_page:
                    break

                current_cursor = connection.page_info.end_cursor
            except ValidationError as e:
                raise LinearClientError(
                    f"Failed to parse issues from API response: {e.errors()[0]['msg']}"
                )

        pagination_info = {
            "hasNextPage": False,
            "endCursor": current_cursor or "",
            "totalFetched": len(all_issues),
        }
        return all_issues, pagination_info

    # Single page fetch
    variables = {
        "filter": filters,
        "first": min(limit, 250),  # Linear API max
        "after": after,
        "includeArchived": include_archived,
        "orderBy": order_by,
    }

    response = self.query(query_str, variables)

    try:
        connection = IssueConnection.model_validate(response.get("issues", {}))
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
    except ValidationError as e:
        raise LinearClientError(
            f"Failed to parse issues from API response: {e.errors()[0]['msg']}"
        )


def get_issue(self: "LinearClient", issue_id: str) -> Issue:
    """Get a single issue by ID or identifier.

    Args:
        issue_id: Issue ID (UUID) or identifier (e.g., 'ENG-123')

    Returns:
        Issue object

    Raises:
        LinearClientError: If the query fails, issue not found, or data validation fails
    """
    # GraphQL query
    query = """
    query Issue($id: String!) {
      issue(id: $id) {
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
        startedAt
        canceledAt
        autoArchivedAt
        dueDate
        estimate
        state {
          id
          name
          type
          color
        }
        assignee {
          id
          name
          displayName
          email
          active
          admin
          createdAt
          updatedAt
        }
        creator {
          id
          name
          displayName
          email
          active
          admin
          createdAt
          updatedAt
        }
        project {
          id
          name
          state
          progress
          url
          createdAt
          updatedAt
        }
        team {
          id
          name
          key
          createdAt
          updatedAt
          cyclesEnabled
          private
        }
        cycle {
          id
          name
          number
          startsAt
          endsAt
          progress
          isActive
          isFuture
          isPast
          isNext
          isPrevious
          createdAt
          updatedAt
          team {
            id
            name
            key
            createdAt
            updatedAt
            cyclesEnabled
            private
          }
        }
        parent {
          id
          identifier
          title
          priority
          priorityLabel
          url
          createdAt
          updatedAt
          state {
            id
            name
            type
            color
          }
          team {
            id
            name
            key
            createdAt
            updatedAt
            cyclesEnabled
            private
          }
        }
        labels {
          nodes {
            id
            name
            color
            createdAt
            updatedAt
          }
        }
        comments {
          nodes {
            id
            body
            createdAt
            updatedAt
            user {
              id
              name
              displayName
              email
              active
              admin
              createdAt
              updatedAt
            }
          }
        }
        attachments {
          nodes {
            id
            title
            url
            createdAt
          }
        }
        subscribers {
          nodes {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
        }
      }
    }
    """

    variables = {"id": issue_id}

    response = self.query(query, variables)

    if not response.get("issue"):
        raise LinearClientError(f"Issue '{issue_id}' not found")

    try:
        return Issue.model_validate(response["issue"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse issue '{issue_id}': {error_details['msg']} at {field_path}"
        )


def create_issue(
    self: "LinearClient",
    title: str,
    team_id: str,
    description: str | None = None,
    assignee_id: str | None = None,
    priority: int | None = None,
    label_ids: list[str] | None = None,
    project_id: str | None = None,
    state_id: str | None = None,
    estimate: int | None = None,
    due_date: str | None = None,
    parent_id: str | None = None,
    cycle_id: str | None = None,
) -> Issue:
    """Create a new issue.

    Args:
        title: Issue title (required)
        team_id: Team UUID (required)
        description: Issue description
        assignee_id: Assignee user UUID
        priority: Priority 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
        label_ids: List of label UUIDs
        project_id: Project UUID
        state_id: Workflow state UUID
        estimate: Story points
        due_date: Due date (ISO format)
        parent_id: Parent issue UUID (for sub-issues)
        cycle_id: Cycle UUID

    Returns:
        Created Issue object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          description
          url
          priority
          priorityLabel
          createdAt
          updatedAt
          state {
            id
            name
            type
            color
          }
          assignee {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
          team {
            id
            name
            key
            createdAt
            updatedAt
            cyclesEnabled
            private
          }
          labels {
            nodes {
              id
              name
              color
              createdAt
              updatedAt
            }
          }
        }
      }
    }
    """

    # Build input object
    input_data: dict[str, Any] = {
        "title": title,
        "teamId": team_id,
    }

    # Add optional fields if provided
    if description:
        input_data["description"] = description
    if assignee_id:
        input_data["assigneeId"] = assignee_id
    if priority is not None:
        input_data["priority"] = priority
    if label_ids:
        input_data["labelIds"] = label_ids
    if project_id:
        input_data["projectId"] = project_id
    if state_id:
        input_data["stateId"] = state_id
    if estimate is not None:
        input_data["estimate"] = estimate
    if due_date:
        input_data["dueDate"] = due_date
    if parent_id:
        input_data["parentId"] = parent_id
    if cycle_id:
        input_data["cycleId"] = cycle_id

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    issue_create = response.get("issueCreate", {})
    if not issue_create.get("success"):
        raise LinearClientError("Failed to create issue")

    try:
        return Issue.model_validate(issue_create["issue"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created issue: {error_details['msg']} at {field_path}"
        )


def update_issue(
    self: "LinearClient",
    issue_id: str,
    title: str | None = None,
    description: str | None = None,
    assignee_id: str | None = None,
    priority: int | None = None,
    label_ids: list[str] | None = None,
    project_id: str | None = None,
    state_id: str | None = None,
    estimate: int | None = None,
    due_date: str | None = None,
    parent_id: str | None = None,
    cycle_id: str | None = None,
) -> Issue:
    """Update an existing issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)
        title: New issue title
        description: New issue description (None = no change, explicit None via API = clear)
        assignee_id: New assignee UUID (None = no change, explicit None via API = unassign)
        priority: New priority 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low
        label_ids: New list of label UUIDs (replaces all labels)
        project_id: New project UUID (None = no change, explicit None via API = remove)
        state_id: New workflow state UUID
        estimate: New story points (None = no change, explicit None via API = clear)
        due_date: New due date (ISO format)
        parent_id: New parent issue UUID
        cycle_id: New cycle UUID

    Returns:
        Updated Issue object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          identifier
          title
          description
          url
          priority
          priorityLabel
          createdAt
          updatedAt
          estimate
          state {
            id
            name
            type
            color
          }
          assignee {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
          }
          team {
            id
            name
            key
            createdAt
            updatedAt
            cyclesEnabled
            private
          }
          project {
            id
            name
            state
            progress
            url
            createdAt
            updatedAt
          }
          labels {
            nodes {
              id
              name
              color
              createdAt
              updatedAt
            }
          }
        }
      }
    }
    """

    # Build input object - only include provided fields (selective field inclusion)
    input_data: dict[str, Any] = {}

    if title is not None:
        input_data["title"] = title
    if description is not None:
        input_data["description"] = description
    if assignee_id is not None:
        input_data["assigneeId"] = assignee_id
    if priority is not None:
        input_data["priority"] = priority
    if label_ids is not None:
        input_data["labelIds"] = label_ids
    if project_id is not None:
        input_data["projectId"] = project_id
    if state_id is not None:
        input_data["stateId"] = state_id
    if estimate is not None:
        input_data["estimate"] = estimate
    if due_date is not None:
        input_data["dueDate"] = due_date
    if parent_id is not None:
        input_data["parentId"] = parent_id
    if cycle_id is not None:
        input_data["cycleId"] = cycle_id

    variables = {
        "id": issue_id,
        "input": input_data,
    }

    response = self.query(mutation, variables)

    # Check if mutation was successful
    issue_update = response.get("issueUpdate", {})
    if not issue_update.get("success"):
        raise LinearClientError("Failed to update issue")

    try:
        return Issue.model_validate(issue_update["issue"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse updated issue: {error_details['msg']} at {field_path}"
        )


def delete_issue(self: "LinearClient", issue_id: str) -> bool:
    """Delete (trash) an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation IssueDelete($id: String!) {
      issueDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": issue_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    issue_delete = response.get("issueDelete", {})
    if not issue_delete.get("success"):
        raise LinearClientError("Failed to delete issue")

    return True


def archive_issue(self: "LinearClient", issue_id: str) -> bool:
    """Archive an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation IssueArchive($id: String!) {
      issueArchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": issue_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    issue_archive = response.get("issueArchive", {})
    if not issue_archive.get("success"):
        raise LinearClientError("Failed to archive issue")

    return True


def unarchive_issue(self: "LinearClient", issue_id: str) -> bool:
    """Unarchive an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation IssueUnarchive($id: String!) {
      issueUnarchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": issue_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    issue_unarchive = response.get("issueUnarchive", {})
    if not issue_unarchive.get("success"):
        raise LinearClientError("Failed to unarchive issue")

    return True


def list_issue_relations(
    self: "LinearClient",
    issue_id: str,
) -> list[Any]:
    """List all relations for an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)

    Returns:
        List of IssueRelation objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    from linear.models import IssueRelationConnection

    query = """
    query IssueRelations($id: String!) {
      issue(id: $id) {
        relations {
          nodes {
            id
            type
            createdAt
            updatedAt
            issue {
              id
              identifier
              title
              url
              priority
              priorityLabel
              createdAt
              updatedAt
              state {
                id
                name
                type
                color
              }
              team {
                id
                name
                key
                createdAt
                updatedAt
                cyclesEnabled
                private
              }
            }
            relatedIssue {
              id
              identifier
              title
              url
              priority
              priorityLabel
              createdAt
              updatedAt
              state {
                id
                name
                type
                color
              }
              team {
                id
                name
                key
                createdAt
                updatedAt
                cyclesEnabled
                private
              }
            }
          }
        }
      }
    }
    """

    variables = {"id": issue_id}
    response = self.query(query, variables)

    if not response.get("issue"):
        raise LinearClientError(f"Issue '{issue_id}' not found")

    try:
        relations_data = response["issue"].get("relations", {})
        connection = IssueRelationConnection.model_validate(relations_data)
        return connection.nodes
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse issue relations: {error_details['msg']} at {field_path}"
        )


def create_issue_relation(
    self: "LinearClient",
    issue_id: str,
    related_issue_id: str,
    relation_type: str,
) -> Any:
    """Create a relation between two issues.

    Args:
        issue_id: Source issue UUID (not identifier - must be resolved first)
        related_issue_id: Target issue UUID (not identifier - must be resolved first)
        relation_type: Type of relation (blocks, blocked, related, duplicate)

    Returns:
        Created IssueRelation object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    from linear.models import IssueRelation

    mutation = """
    mutation IssueRelationCreate($input: IssueRelationCreateInput!) {
      issueRelationCreate(input: $input) {
        success
        issueRelation {
          id
          type
          createdAt
          updatedAt
          issue {
            id
            identifier
            title
            url
            priority
            priorityLabel
            createdAt
            updatedAt
            state {
              id
              name
              type
              color
            }
            team {
              id
              name
              key
              createdAt
              updatedAt
              cyclesEnabled
              private
            }
          }
          relatedIssue {
            id
            identifier
            title
            url
            priority
            priorityLabel
            createdAt
            updatedAt
            state {
              id
              name
              type
              color
            }
            team {
              id
              name
              key
              createdAt
              updatedAt
              cyclesEnabled
              private
            }
          }
        }
      }
    }
    """

    input_data = {
        "issueId": issue_id,
        "relatedIssueId": related_issue_id,
        "type": relation_type,
    }

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    relation_create = response.get("issueRelationCreate", {})
    if not relation_create.get("success"):
        raise LinearClientError("Failed to create issue relation")

    try:
        return IssueRelation.model_validate(relation_create["issueRelation"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created issue relation: {error_details['msg']} at {field_path}"
        )


def delete_issue_relation(self: "LinearClient", relation_id: str) -> bool:
    """Delete a relation between issues.

    Args:
        relation_id: IssueRelation UUID

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation IssueRelationDelete($id: String!) {
      issueRelationDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": relation_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    relation_delete = response.get("issueRelationDelete", {})
    if not relation_delete.get("success"):
        raise LinearClientError("Failed to delete issue relation")

    return True


def duplicate_issue(
    self: "LinearClient",
    issue_id: str,
    create_relation: bool = False,
) -> Issue:
    """Duplicate an issue by creating a copy with the same fields.

    Args:
        issue_id: Source issue ID or identifier
        create_relation: If True, create a 'duplicate' relation between issues

    Returns:
        Newly created Issue object

    Raises:
        LinearClientError: If source issue not found or creation fails
    """
    # Fetch the source issue
    source_issue = get_issue(self, issue_id)

    # Extract copyable fields from source
    # Title with "Copy of " prefix to distinguish the duplicate
    title = f"Copy of {source_issue.title}"
    description = source_issue.description
    priority = source_issue.priority
    team_id = source_issue.team.id

    # Team ID should always exist for an issue, but type system requires check
    if not team_id:
        raise LinearClientError(f"Issue '{issue_id}' has no team ID")

    # Extract label IDs from labels list
    label_ids = None
    if source_issue.labels:
        label_ids = [label.id for label in source_issue.labels]

    # Extract optional fields (only if they exist)
    project_id = source_issue.project.id if source_issue.project else None
    state_id = source_issue.state.id if source_issue.state else None
    estimate = source_issue.estimate
    # Convert datetime to ISO string format for due_date
    due_date = source_issue.due_date.isoformat() if source_issue.due_date else None
    parent_id = source_issue.parent.id if source_issue.parent else None
    cycle_id = source_issue.cycle.id if source_issue.cycle else None

    # Create the duplicate issue
    # Note: assignee is intentionally NOT copied - new issue starts unassigned
    new_issue = create_issue(
        self,
        title=title,
        team_id=team_id,
        description=description,
        priority=priority,
        label_ids=label_ids,
        project_id=project_id,
        state_id=state_id,
        estimate=estimate,
        due_date=due_date,
        parent_id=parent_id,
        cycle_id=cycle_id,
    )

    # Optionally create a duplicate relation
    if create_relation:
        create_issue_relation(
            self,
            issue_id=source_issue.id,
            related_issue_id=new_issue.id,
            relation_type="duplicate",
        )

    return new_issue
