"""Cycle-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import PageInfo


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
    team: "Team"  # Forward reference
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


# Import Team for forward reference
from .teams import Team  # noqa: E402

Cycle.model_rebuild()


class CycleConnection(BaseModel):
    """Paginated cycle list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Cycle] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
