"""Issue-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING

from pydantic import ValidationError

from linear.models import Issue, IssueConnection

if TYPE_CHECKING:
    from .client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_issues(
    self: "LinearClient",
    assignee: str | None = None,
    project: str | None = None,
    status: str | None = None,
    team: str | None = None,
    priority: int | None = None,
    labels: list[str] | None = None,
    limit: int = 50,
    include_archived: bool = False,
    sort: str = "updated",
) -> list[Issue]:
    """List issues with optional filters.

    Args:
        assignee: Filter by assignee email
        project: Filter by project name
        status: Filter by issue status/state
        team: Filter by team key (e.g., ENG, DESIGN)
        priority: Filter by priority (0-4)
        labels: Filter by label names
        limit: Maximum number of issues to return (default: 50)
        include_archived: Include archived issues (default: False)
        sort: Sort field: created, updated, priority (default: updated)

    Returns:
        List of Issue objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # Build filter object
    filters = {}

    if assignee:
        filters["assignee"] = {"email": {"eq": assignee}}

    if project:
        # Support both UUID and name matching
        if len(project) == 36 and "-" in project:  # Simple UUID check
            filters["project"] = {"id": {"eq": project}}
        else:
            filters["project"] = {"name": {"contains": project}}

    if status:
        filters["state"] = {"name": {"eqIgnoreCase": status}}

    if team:
        # Filter by team key only (keys are unique identifiers)
        filters["team"] = {"key": {"eqIgnoreCase": team}}

    if priority is not None:
        filters["priority"] = {"eq": priority}

    if labels:
        filters["labels"] = {"name": {"in": labels}}

    # Determine order by
    order_by_map = {
        "created": "createdAt",
        "updated": "updatedAt",
        "priority": "priority",
    }
    order_by = order_by_map.get(sort, "updatedAt")

    # GraphQL query
    query = """
    query Issues($filter: IssueFilter, $first: Int, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
      issues(filter: $filter, first: $first, includeArchived: $includeArchived, orderBy: $orderBy) {
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

    variables = {
        "filter": filters if filters else None,
        "first": min(limit, 250),  # Linear API max
        "includeArchived": include_archived,
        "orderBy": order_by,
    }

    response = self.query(query, variables)

    try:
        connection = IssueConnection.model_validate(response.get("issues", {}))
        return connection.nodes
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse issues from API response: {error_details['msg']} at {field_path}"
        )


def search_issues(
    self: "LinearClient",
    query: str,
    limit: int = 50,
    include_archived: bool = False,
    sort: str = "updated",
) -> list[Issue]:
    """Search issues by title.

    Args:
        query: Search query (searches issue titles, case-insensitive)
        limit: Maximum number of issues to return (default: 50)
        include_archived: Include archived issues (default: False)
        sort: Sort field: created, updated, priority (default: updated)

    Returns:
        List of matching Issue objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    # Build filter with title search
    filters = {"title": {"containsIgnoreCase": query}}

    # Determine order by
    order_by_map = {
        "created": "createdAt",
        "updated": "updatedAt",
        "priority": "priority",
    }
    order_by = order_by_map.get(sort, "updatedAt")

    # GraphQL query (same as list_issues)
    query_str = """
    query Issues($filter: IssueFilter, $first: Int, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
      issues(filter: $filter, first: $first, includeArchived: $includeArchived, orderBy: $orderBy) {
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

    variables = {
        "filter": filters,
        "first": min(limit, 250),  # Linear API max
        "includeArchived": include_archived,
        "orderBy": order_by,
    }

    response = self.query(query_str, variables)

    try:
        connection = IssueConnection.model_validate(response.get("issues", {}))
        return connection.nodes
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
    input_data = {
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
    input_data = {}

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
