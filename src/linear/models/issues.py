"""Issue-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from linear.models.base import PageInfo


class WorkflowState(BaseModel):
    """Represents a workflow state (backlog, unstarted, started, completed, canceled)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    type: str
    color: Optional[str] = None


class Comment(BaseModel):
    """Represents an issue comment."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    body: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    user: "User"  # Forward reference


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

    # Nested objects - using forward references
    state: WorkflowState
    assignee: Optional["User"] = None
    creator: Optional["User"] = None
    team: "Team"
    project: Optional["Project"] = None
    cycle: Optional["Cycle"] = None
    parent: Optional["Issue"] = None  # Self-referential for sub-issues
    labels: list["Label"] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)
    subscribers: list["User"] = Field(default_factory=list)

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


# Import dependencies for forward references
from linear.models.users import User  # noqa: E402
from linear.models.teams import Team  # noqa: E402
from linear.models.projects import Project  # noqa: E402
from linear.models.cycles import Cycle  # noqa: E402
from linear.models.labels import Label  # noqa: E402

# Rebuild models to resolve forward references
Comment.model_rebuild()
Issue.model_rebuild()


class IssueRelation(BaseModel):
    """Represents a relation between two issues."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    issue: "Issue"
    related_issue: "Issue" = Field(alias="relatedIssue")


# Rebuild IssueRelation to resolve forward references
IssueRelation.model_rebuild()


class IssueConnection(BaseModel):
    """Paginated issue list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Issue] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")


class IssueRelationConnection(BaseModel):
    """Paginated issue relation list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[IssueRelation] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
