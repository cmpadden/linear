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
