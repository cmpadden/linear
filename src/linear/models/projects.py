"""Project-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from .base import PageInfo


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
    lead: Optional["User"] = None  # Forward reference
    creator: Optional["User"] = None  # Forward reference
    teams: list["Team"] = Field(default_factory=list)  # Forward reference

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


# Import User and Team for forward references
from .users import User  # noqa: E402
from .teams import Team  # noqa: E402

Project.model_rebuild()


class ProjectConnection(BaseModel):
    """Paginated project list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Project] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
