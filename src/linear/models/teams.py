"""Team-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import Organization, PageInfo


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


class TeamConnection(BaseModel):
    """Paginated team list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Team] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
