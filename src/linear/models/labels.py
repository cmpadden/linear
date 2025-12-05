"""Label-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import PageInfo


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
    team: Optional["Team"] = None  # Forward reference
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


# Import Team for forward reference
from .teams import Team  # noqa: E402

Label.model_rebuild()


class LabelConnection(BaseModel):
    """Paginated label list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Label] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
