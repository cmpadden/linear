"""Linear API client for GraphQL interactions."""

import os
from typing import Any

import httpx


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


class LinearClient:
    """Client for interacting with the Linear GraphQL API."""

    API_URL = "https://api.linear.app/graphql"
    RATE_LIMIT = 1500  # requests per hour

    def __init__(self, api_key: str | None = None):
        """Initialize the Linear client.

        Args:
            api_key: Linear API key. If not provided, will read from LINEAR_API_KEY env var.

        Raises:
            LinearClientError: If no API key is provided or found.
        """
        self.api_key = api_key or os.getenv("LINEAR_API_KEY")
        if not self.api_key:
            raise LinearClientError(
                "No API key provided. Set LINEAR_API_KEY environment variable or pass api_key parameter.\n"
                "Get your API key at: https://linear.app/settings/api"
            )

        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    def query(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Query response data

        Raises:
            LinearClientError: If the query fails
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.API_URL, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                if "errors" in data:
                    errors = data["errors"]
                    error_messages = [e.get("message", str(e)) for e in errors]
                    raise LinearClientError(
                        f"GraphQL errors: {', '.join(error_messages)}"
                    )

                return data.get("data", {})

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise LinearClientError(
                    "Authentication failed. Check your API key.\n"
                    "Get your API key at: https://linear.app/settings/api"
                )
            elif e.response.status_code == 429:
                raise LinearClientError(
                    f"Rate limit exceeded. Linear API allows {self.RATE_LIMIT} requests per hour.\n"
                    "Please wait before making more requests."
                )
            else:
                raise LinearClientError(
                    f"HTTP error: {e.response.status_code} - {e.response.text}"
                )
        except httpx.RequestError as e:
            raise LinearClientError(f"Network error: {str(e)}")

    def list_issues(
        self,
        assignee: str | None = None,
        project: str | None = None,
        status: str | None = None,
        team: str | None = None,
        priority: int | None = None,
        labels: list[str] | None = None,
        limit: int = 50,
        include_archived: bool = False,
        sort: str = "updated",
    ) -> dict[str, Any]:
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
            Query response containing issues

        Raises:
            LinearClientError: If the query fails
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
                name
                type
              }
              assignee {
                name
                email
              }
              project {
                name
              }
              team {
                name
                key
              }
              cycle {
                id
                name
                number
              }
              labels {
                nodes {
                  name
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

        return self.query(query, variables)

    def search_issues(
        self,
        query: str,
        limit: int = 50,
        include_archived: bool = False,
        sort: str = "updated",
    ) -> dict[str, Any]:
        """Search issues by title.

        Args:
            query: Search query (searches issue titles, case-insensitive)
            limit: Maximum number of issues to return (default: 50)
            include_archived: Include archived issues (default: False)
            sort: Sort field: created, updated, priority (default: updated)

        Returns:
            Query response containing matching issues

        Raises:
            LinearClientError: If the query fails
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
                name
                type
              }
              assignee {
                name
                email
              }
              project {
                name
              }
              team {
                name
                key
              }
              cycle {
                id
                name
                number
              }
              labels {
                nodes {
                  name
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

        return self.query(query_str, variables)

    def get_issue(self, issue_id: str) -> dict[str, Any]:
        """Get a single issue by ID or identifier.

        Args:
            issue_id: Issue ID (UUID) or identifier (e.g., 'ENG-123')

        Returns:
            Query response containing the issue

        Raises:
            LinearClientError: If the query fails or issue not found
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
              name
              type
              color
            }
            assignee {
              name
              email
              avatarUrl
            }
            creator {
              name
              email
            }
            project {
              name
              url
            }
            team {
              name
              key
            }
            cycle {
              name
              number
            }
            parent {
              identifier
              title
            }
            labels {
              nodes {
                name
                color
              }
            }
            comments {
              nodes {
                body
                createdAt
                user {
                  name
                }
              }
            }
            attachments {
              nodes {
                title
                url
              }
            }
            subscribers {
              nodes {
                name
              }
            }
          }
        }
        """

        variables = {"id": issue_id}

        response = self.query(query, variables)

        if not response.get("issue"):
            raise LinearClientError(f"Issue '{issue_id}' not found")

        return response

    def list_projects(
        self,
        state: str | None = None,
        team: str | None = None,
        limit: int = 50,
        include_archived: bool = False,
        sort: str = "updated",
    ) -> dict[str, Any]:
        """List projects with optional filters.

        Args:
            state: Filter by project state (planned, started, paused, completed, canceled)
            team: Filter by team name or key
            limit: Maximum number of projects to return (default: 50)
            include_archived: Include archived projects (default: False)
            sort: Sort field: created, updated (default: updated)

        Returns:
            Query response containing projects

        Raises:
            LinearClientError: If the query fails
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
        query Projects($filter: ProjectFilter, $first: Int, $includeArchived: Boolean, $orderBy: PaginationOrderBy) {
          projects(filter: $filter, first: $first, includeArchived: $includeArchived, orderBy: $orderBy) {
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

        variables = {
            "filter": filters if filters else None,
            "first": min(limit, 250),  # Linear API max
            "includeArchived": include_archived,
            "orderBy": order_by,
        }

        return self.query(query, variables)

    def get_project(self, project_id: str) -> dict[str, Any]:
        """Get a single project by ID or slug.

        Args:
            project_id: Project ID (UUID) or slug

        Returns:
            Query response containing the project

        Raises:
            LinearClientError: If the query fails or project not found
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

        return response

    def list_teams(
        self,
        limit: int = 50,
        include_archived: bool = False,
    ) -> dict[str, Any]:
        """List teams in the workspace.

        Args:
            limit: Maximum number of teams to return (default: 50)
            include_archived: Include archived teams (default: False)

        Returns:
            Query response containing teams

        Raises:
            LinearClientError: If the query fails
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

        return self.query(query, variables)

    def get_team(self, team_id: str) -> dict[str, Any]:
        """Get a single team by ID or key.

        Args:
            team_id: Team ID (UUID) or key (e.g., 'ENG')

        Returns:
            Query response containing the team

        Raises:
            LinearClientError: If the query fails or team not found
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

        return response

    def list_cycles(
        self,
        team: str | None = None,
        active: bool = False,
        future: bool = False,
        past: bool = False,
        limit: int = 50,
        include_archived: bool = False,
    ) -> dict[str, Any]:
        """List cycles with optional filters.

        Args:
            team: Filter by team name or key
            active: Show only active cycles
            future: Show only future cycles
            past: Show only past cycles
            limit: Maximum number of cycles to return (default: 50)
            include_archived: Include archived cycles (default: False)

        Returns:
            Query response containing cycles

        Raises:
            LinearClientError: If the query fails
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

        return self.query(query, variables)

    def get_cycle(self, cycle_id: str) -> dict[str, Any]:
        """Get a single cycle by ID.

        Args:
            cycle_id: Cycle ID (UUID)

        Returns:
            Query response containing the cycle

        Raises:
            LinearClientError: If the query fails or cycle not found
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

        return response

    def list_users(
        self,
        active_only: bool = True,
        limit: int = 50,
        include_disabled: bool = False,
    ) -> dict[str, Any]:
        """List users in the workspace.

        Args:
            active_only: Show only active users (default: True)
            limit: Maximum number of users to return (default: 50)
            include_disabled: Include disabled users (default: False)

        Returns:
            Query response containing users

        Raises:
            LinearClientError: If the query fails
        """
        query = """
        query Users($filter: UserFilter, $first: Int, $includeDisabled: Boolean) {
          users(filter: $filter, first: $first, includeDisabled: $includeDisabled) {
            nodes {
              id
              name
              displayName
              email
              active
              admin
              createdAt
              updatedAt
              avatarUrl
              timezone
              organization {
                id
                name
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

        if active_only:
            filters["active"] = {"eq": True}

        variables = {
            "filter": filters if filters else None,
            "first": min(limit, 250),  # Linear API max
            "includeDisabled": include_disabled,
        }

        return self.query(query, variables)

    def get_user(self, user_id: str) -> dict[str, Any]:
        """Get a single user by ID or email.

        Args:
            user_id: User ID (UUID) or email

        Returns:
            Query response containing the user

        Raises:
            LinearClientError: If the query fails or user not found
        """
        query = """
        query User($id: String!) {
          user(id: $id) {
            id
            name
            displayName
            email
            active
            admin
            createdAt
            updatedAt
            avatarUrl
            timezone
            description
            statusEmoji
            statusLabel
            statusUntilAt
            organization {
              id
              name
              urlKey
            }
            teams {
              nodes {
                id
                name
                key
              }
            }
            assignedIssues(first: 10, filter: { state: { type: { in: ["started", "unstarted"] } } }) {
              nodes {
                id
                identifier
                title
                priority
                priorityLabel
                state {
                  name
                  type
                }
              }
            }
            createdIssues(first: 5) {
              nodes {
                id
                identifier
                title
              }
            }
          }
        }
        """

        variables = {"id": user_id}

        response = self.query(query, variables)

        if not response.get("user"):
            raise LinearClientError(f"User '{user_id}' not found")

        return response

    def list_labels(
        self,
        limit: int = 50,
        team: str | None = None,
        include_archived: bool = False,
    ) -> dict[str, Any]:
        """List issue labels.

        Args:
            limit: Maximum number of labels to return (default: 50)
            team: Filter by team ID or key
            include_archived: Include archived labels (default: False)

        Returns:
            GraphQL response with labels data

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

        return self.query(query, variables)

    def get_viewer(self) -> dict[str, Any]:
        """Get the current authenticated user.

        Returns:
            Query response containing viewer (current user) data

        Raises:
            LinearClientError: If the query fails
        """
        query = """
        query {
          viewer {
            id
            name
            email
            teams {
              nodes {
                id
                key
                name
              }
            }
          }
        }
        """
        return self.query(query)

    def create_issue(
        self,
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
    ) -> dict[str, Any]:
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
            Mutation response containing created issue data

        Raises:
            LinearClientError: If the mutation fails
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
              state {
                name
                type
              }
              assignee {
                name
                email
              }
              team {
                name
                key
              }
              labels {
                nodes {
                  name
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

        return response
