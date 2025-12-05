"""Pydantic models for Linear entities with full type validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PageInfo(BaseModel):
    """GraphQL pagination info."""

    model_config = ConfigDict(populate_by_name=True)

    has_next_page: bool = Field(default=False, alias="hasNextPage")
    end_cursor: Optional[str] = Field(None, alias="endCursor")


class Organization(BaseModel):
    """Represents a Linear organization."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    url_key: Optional[str] = Field(None, alias="urlKey")


class WorkflowState(BaseModel):
    """Represents a workflow state (backlog, unstarted, started, completed, canceled)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    type: str
    color: Optional[str] = None


class User(BaseModel):
    """Represents a Linear user."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    name: str
    display_name: Optional[str] = Field(None, alias="displayName")
    email: str
    active: bool = True
    admin: bool = False
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    avatar_url: Optional[HttpUrl] = Field(None, alias="avatarUrl")
    timezone: Optional[str] = None
    description: Optional[str] = None
    status_emoji: Optional[str] = Field(None, alias="statusEmoji")
    status_label: Optional[str] = Field(None, alias="statusLabel")
    status_until_at: Optional[datetime] = Field(None, alias="statusUntilAt")
    organization: Optional[Organization] = None

    def format_status(self) -> str:
        """Get user status string."""
        return "Inactive" if not self.active else "Active"

    def format_role(self) -> str:
        """Get user role string."""
        return "Admin" if self.admin else "Member"

    def format_created_at(self) -> str:
        """Get formatted creation date."""
        return self.created_at.strftime("%Y-%m-%d") if self.created_at else ""


class Team(BaseModel):
    """Represents a Linear team."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    name: str
    key: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    private: bool = False
    archived_at: Optional[datetime] = Field(None, alias="archivedAt")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    cycles_enabled: bool = Field(default=False, alias="cyclesEnabled")
    timezone: Optional[str] = None
    organization: Optional[Organization] = None

    @property
    def archived(self) -> bool:
        """Check if team is archived."""
        return self.archived_at is not None

    def format_members_count(self, count: int) -> str:
        """Get formatted members count."""
        return f"{count} member{'s' if count != 1 else ''}"

    def format_issues_count(self, count: int) -> str:
        """Get formatted issues count."""
        return f"{count} issue{'s' if count != 1 else ''}"

    def format_projects_count(self, count: int) -> str:
        """Get formatted projects count."""
        return f"{count} project{'s' if count != 1 else ''}"

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        return self.updated_at.strftime("%Y-%m-%d") if self.updated_at else ""


class Label(BaseModel):
    """Represents a Linear issue label."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    archived_at: Optional[datetime] = Field(None, alias="archivedAt")
    team: Optional[Team] = None
    parent: Optional["Label"] = None  # Self-referential

    def format_team(self) -> str:
        """Get formatted team string."""
        if self.team and self.team.key:
            return self.team.key
        elif self.team and self.team.name:
            return self.team.name
        return "All teams"

    def format_issues_count(self, count: int) -> str:
        """Get formatted issues count."""
        return f"{count} issue{'s' if count != 1 else ''}"

    def format_created_at(self) -> str:
        """Get formatted creation date."""
        return self.created_at.strftime("%Y-%m-%d") if self.created_at else ""


# Enable self-referential Label.parent
Label.model_rebuild()


class Project(BaseModel):
    """Represents a Linear project."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    state: str
    progress: float = Field(default=0.0)
    start_date: Optional[datetime] = Field(None, alias="startDate")
    target_date: Optional[datetime] = Field(None, alias="targetDate")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    canceled_at: Optional[datetime] = Field(None, alias="canceledAt")
    url: HttpUrl
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    archived_at: Optional[datetime] = Field(None, alias="archivedAt")
    color: Optional[str] = None
    icon: Optional[str] = None
    slug_id: Optional[str] = Field(None, alias="slugId")
    lead: Optional[User] = None
    creator: Optional[User] = None
    teams: list[Team] = Field(default_factory=list)

    @field_validator("teams", mode="before")
    @classmethod
    def extract_teams_nodes(cls, v):
        """Extract nodes from GraphQL connection pattern."""
        if isinstance(v, dict) and "nodes" in v:
            return v["nodes"]
        return v or []

    def format_lead(self) -> str:
        """Get formatted lead string."""
        return self.lead.name if self.lead else "No lead"

    def format_progress(self) -> str:
        """Get formatted progress percentage."""
        return f"{self.progress * 100:.0f}%"

    def format_date(self, date_value: Optional[datetime]) -> str:
        """Get formatted date."""
        if not date_value:
            return ""
        return date_value.strftime("%Y-%m-%d")

    def format_start_date(self) -> str:
        """Get formatted start date."""
        return self.format_date(self.start_date) if self.start_date else "Not set"

    def format_target_date(self) -> str:
        """Get formatted target date."""
        return self.format_date(self.target_date) if self.target_date else "Not set"

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        return self.format_date(self.updated_at)


class Cycle(BaseModel):
    """Represents a Linear cycle."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    number: int
    name: Optional[str] = None
    description: Optional[str] = None
    starts_at: datetime = Field(alias="startsAt")
    ends_at: datetime = Field(alias="endsAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    archived_at: Optional[datetime] = Field(None, alias="archivedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    is_active: bool = Field(default=False, alias="isActive")
    is_future: bool = Field(default=False, alias="isFuture")
    is_past: bool = Field(default=False, alias="isPast")
    is_next: bool = Field(default=False, alias="isNext")
    is_previous: bool = Field(default=False, alias="isPrevious")
    progress: float = Field(default=0.0)
    team: Team
    scope_history: Optional[list[int]] = Field(None, alias="scopeHistory")
    issue_count_history: Optional[list[int]] = Field(None, alias="issueCountHistory")
    completed_scope_history: Optional[list[int]] = Field(
        None, alias="completedScopeHistory"
    )

    def format_progress(self) -> str:
        """Get formatted progress percentage."""
        return f"{self.progress * 100:.0f}%"

    def format_status(self) -> str:
        """Get cycle status string."""
        if self.is_active:
            return "Active"
        elif self.is_future:
            return "Future"
        elif self.is_past:
            return "Past"
        return "Unknown"

    def format_date(self, date_value: Optional[datetime]) -> str:
        """Get formatted date."""
        if not date_value:
            return ""
        return date_value.strftime("%Y-%m-%d")

    def format_starts_at(self) -> str:
        """Get formatted start date."""
        return self.format_date(self.starts_at)

    def format_ends_at(self) -> str:
        """Get formatted end date."""
        return self.format_date(self.ends_at)


class Comment(BaseModel):
    """Represents an issue comment."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    body: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    user: User


class Attachment(BaseModel):
    """Represents an issue attachment."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    url: HttpUrl
    created_at: datetime = Field(alias="createdAt")


class Issue(BaseModel):
    """Represents a Linear issue."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    identifier: str
    title: str
    description: Optional[str] = None
    priority: int = Field(default=0)
    priority_label: str = Field(alias="priorityLabel")
    url: HttpUrl
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    canceled_at: Optional[datetime] = Field(None, alias="canceledAt")
    auto_archived_at: Optional[datetime] = Field(None, alias="autoArchivedAt")
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    estimate: Optional[int] = None

    # Nested objects
    state: WorkflowState
    assignee: Optional[User] = None
    creator: Optional[User] = None
    team: Team
    project: Optional[Project] = None
    cycle: Optional[Cycle] = None
    parent: Optional["Issue"] = None  # Self-referential for sub-issues
    labels: list[Label] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)
    subscribers: list[User] = Field(default_factory=list)

    @field_validator("labels", "comments", "attachments", "subscribers", mode="before")
    @classmethod
    def extract_nodes(cls, v):
        """Extract nodes from GraphQL connection pattern."""
        if isinstance(v, dict) and "nodes" in v:
            return v["nodes"]
        return v or []

    def format_short_id(self) -> str:
        """Get short identifier (e.g., 'BLA-123')."""
        return self.identifier

    def format_assignee(self) -> str:
        """Get formatted assignee string."""
        return self.assignee.name if self.assignee else "Unassigned"

    def format_labels(self) -> str:
        """Get comma-separated labels."""
        return ", ".join(label.name for label in self.labels) if self.labels else ""

    def format_created_date(self) -> str:
        """Get formatted creation date."""
        return self.created_at.strftime("%Y-%m-%d")

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        return self.updated_at.strftime("%Y-%m-%d") if self.updated_at else ""


# Enable self-referential Issue.parent
Issue.model_rebuild()


class IssueConnection(BaseModel):
    """Paginated issue list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Issue] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")


class ProjectConnection(BaseModel):
    """Paginated project list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Project] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")


class TeamConnection(BaseModel):
    """Paginated team list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Team] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")


class CycleConnection(BaseModel):
    """Paginated cycle list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Cycle] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")


class UserConnection(BaseModel):
    """Paginated user list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[User] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")


class LabelConnection(BaseModel):
    """Paginated label list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Label] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
