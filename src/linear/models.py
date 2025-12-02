"""Data models for Linear entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Issue:
    """Represents a Linear issue."""

    id: str
    identifier: str
    title: str
    description: str | None
    priority: int
    priority_label: str
    url: str
    created_at: str
    updated_at: str
    completed_at: str | None
    state_name: str
    state_type: str
    assignee_name: str | None
    assignee_email: str | None
    project_name: str | None
    team_name: str
    team_key: str
    labels: list[str]

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Issue":
        """Create an Issue from API response data.

        Args:
            data: Issue data from GraphQL response

        Returns:
            Issue instance
        """
        assignee = data.get("assignee")
        project = data.get("project")
        team = data.get("team", {})
        labels_data = data.get("labels", {}).get("nodes", [])
        state = data.get("state", {})

        return cls(
            id=data.get("id", ""),
            identifier=data.get("identifier", ""),
            title=data.get("title", ""),
            description=data.get("description"),
            priority=data.get("priority", 0),
            priority_label=data.get("priorityLabel", "No priority"),
            url=data.get("url", ""),
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
            completed_at=data.get("completedAt"),
            state_name=state.get("name", ""),
            state_type=state.get("type", ""),
            assignee_name=assignee.get("name") if assignee else None,
            assignee_email=assignee.get("email") if assignee else None,
            project_name=project.get("name") if project else None,
            team_name=team.get("name", ""),
            team_key=team.get("key", ""),
            labels=[label.get("name", "") for label in labels_data],
        )

    def format_short_id(self) -> str:
        """Get short identifier (e.g., 'BLA-123')."""
        return self.identifier

    def format_assignee(self) -> str:
        """Get formatted assignee string."""
        if self.assignee_name:
            return self.assignee_name
        return "Unassigned"

    def format_labels(self) -> str:
        """Get comma-separated labels."""
        if not self.labels:
            return ""
        return ", ".join(self.labels)

    def format_created_date(self) -> str:
        """Get formatted creation date."""
        try:
            dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return self.created_at

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        try:
            dt = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return self.updated_at


def parse_issues_response(response: dict[str, Any]) -> list[Issue]:
    """Parse issues from API response.

    Args:
        response: GraphQL response data

    Returns:
        List of Issue objects
    """
    issues_data = response.get("issues", {}).get("nodes", [])
    return [Issue.from_api_response(issue_data) for issue_data in issues_data]


@dataclass
class Project:
    """Represents a Linear project."""

    id: str
    name: str
    description: str | None
    state: str
    progress: float
    start_date: str | None
    target_date: str | None
    url: str
    created_at: str
    updated_at: str
    archived_at: str | None
    color: str | None
    icon: str | None
    lead_name: str | None
    lead_email: str | None
    team_name: str
    team_key: str

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Project":
        """Create a Project from API response data.

        Args:
            data: Project data from GraphQL response

        Returns:
            Project instance
        """
        lead = data.get("lead")
        teams_data = data.get("teams", {}).get("nodes", [])
        # Get the first team (projects can be associated with multiple teams)
        team = teams_data[0] if teams_data else {}

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            state=data.get("state", ""),
            progress=data.get("progress", 0.0),
            start_date=data.get("startDate"),
            target_date=data.get("targetDate"),
            url=data.get("url", ""),
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
            archived_at=data.get("archivedAt"),
            color=data.get("color"),
            icon=data.get("icon"),
            lead_name=lead.get("name") if lead else None,
            lead_email=lead.get("email") if lead else None,
            team_name=team.get("name", ""),
            team_key=team.get("key", ""),
        )

    def format_lead(self) -> str:
        """Get formatted lead string."""
        if self.lead_name:
            return self.lead_name
        return "No lead"

    def format_progress(self) -> str:
        """Get formatted progress percentage."""
        return f"{self.progress * 100:.0f}%"

    def format_date(self, date_str: str | None) -> str:
        """Get formatted date."""
        if not date_str:
            return ""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return date_str

    def format_start_date(self) -> str:
        """Get formatted start date."""
        return self.format_date(self.start_date) if self.start_date else "Not set"

    def format_target_date(self) -> str:
        """Get formatted target date."""
        return self.format_date(self.target_date) if self.target_date else "Not set"

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        return self.format_date(self.updated_at)


def parse_projects_response(response: dict[str, Any]) -> list[Project]:
    """Parse projects from API response.

    Args:
        response: GraphQL response data

    Returns:
        List of Project objects
    """
    projects_data = response.get("projects", {}).get("nodes", [])
    return [Project.from_api_response(project_data) for project_data in projects_data]


@dataclass
class Team:
    """Represents a Linear team."""

    id: str
    name: str
    key: str
    description: str | None
    color: str | None
    icon: str | None
    private: bool
    archived: bool
    created_at: str
    updated_at: str
    members_count: int
    issues_count: int
    projects_count: int
    cycles_enabled: bool

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Team":
        """Create a Team from API response data.

        Args:
            data: Team data from GraphQL response

        Returns:
            Team instance
        """
        # Count members, issues, and projects
        members_data = data.get("members", {}).get("nodes", [])
        issues_data = data.get("issues", {}).get("nodes", [])
        projects_data = data.get("projects", {}).get("nodes", [])

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            key=data.get("key", ""),
            description=data.get("description"),
            color=data.get("color"),
            icon=data.get("icon"),
            private=data.get("private", False),
            archived=data.get("archivedAt") is not None,
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
            members_count=len(members_data),
            issues_count=len(issues_data),
            projects_count=len(projects_data),
            cycles_enabled=data.get("cyclesEnabled", False),
        )

    def format_members_count(self) -> str:
        """Get formatted members count."""
        return f"{self.members_count} member{'s' if self.members_count != 1 else ''}"

    def format_issues_count(self) -> str:
        """Get formatted issues count."""
        return f"{self.issues_count} issue{'s' if self.issues_count != 1 else ''}"

    def format_projects_count(self) -> str:
        """Get formatted projects count."""
        return f"{self.projects_count} project{'s' if self.projects_count != 1 else ''}"

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        try:
            dt = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return self.updated_at


def parse_teams_response(response: dict[str, Any]) -> list[Team]:
    """Parse teams from API response.

    Args:
        response: GraphQL response data

    Returns:
        List of Team objects
    """
    teams_data = response.get("teams", {}).get("nodes", [])
    return [Team.from_api_response(team_data) for team_data in teams_data]


@dataclass
class Cycle:
    """Represents a Linear cycle."""

    id: str
    number: int
    name: str
    description: str | None
    starts_at: str
    ends_at: str
    completed_at: str | None
    archived_at: str | None
    created_at: str
    updated_at: str
    is_active: bool
    is_future: bool
    is_past: bool
    is_next: bool
    is_previous: bool
    progress: float
    team_id: str
    team_name: str
    team_key: str
    issues_count: int

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Cycle":
        """Create a Cycle from API response data.

        Args:
            data: Cycle data from GraphQL response

        Returns:
            Cycle instance
        """
        team = data.get("team", {}) or {}
        issues = data.get("issues", {}) or {}
        issues_data = issues.get("nodes") or []

        return cls(
            id=data.get("id", ""),
            number=data.get("number", 0),
            name=data.get("name", ""),
            description=data.get("description"),
            starts_at=data.get("startsAt", ""),
            ends_at=data.get("endsAt", ""),
            completed_at=data.get("completedAt"),
            archived_at=data.get("archivedAt"),
            created_at=data.get("createdAt", ""),
            updated_at=data.get("updatedAt", ""),
            is_active=data.get("isActive", False),
            is_future=data.get("isFuture", False),
            is_past=data.get("isPast", False),
            is_next=data.get("isNext", False),
            is_previous=data.get("isPrevious", False),
            progress=data.get("progress", 0.0),
            team_id=team.get("id", ""),
            team_name=team.get("name", ""),
            team_key=team.get("key", ""),
            issues_count=len(issues_data),
        )

    def format_progress(self) -> str:
        """Get formatted progress percentage."""
        return f"{self.progress * 100:.0f}%"

    def format_date(self, date_str: str | None) -> str:
        """Get formatted date.

        Args:
            date_str: ISO date string

        Returns:
            Formatted date string (YYYY-MM-DD) or empty string
        """
        if not date_str:
            return ""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return date_str

    def format_starts_at(self) -> str:
        """Get formatted start date."""
        return self.format_date(self.starts_at)

    def format_ends_at(self) -> str:
        """Get formatted end date."""
        return self.format_date(self.ends_at)

    def format_status(self) -> str:
        """Get cycle status string."""
        if self.is_active:
            return "Active"
        elif self.is_future:
            return "Future"
        elif self.is_past:
            return "Past"
        else:
            return "Unknown"


def parse_cycles_response(response: dict[str, Any]) -> list[Cycle]:
    """Parse cycles from API response.

    Args:
        response: GraphQL response data

    Returns:
        List of Cycle objects
    """
    cycles_data = response.get("cycles", {}).get("nodes", [])
    return [Cycle.from_api_response(cycle_data) for cycle_data in cycles_data]
