"""Roadmap-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from linear.models.base import PageInfo


class Roadmap(BaseModel):
    """Represents a Linear roadmap."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    slug_id: str = Field(alias="slugId")
    url: HttpUrl
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    archived_at: Optional[datetime] = Field(None, alias="archivedAt")
    creator: Optional["User"] = None  # Forward reference
    owner: Optional["User"] = None  # Forward reference

    def format_date(self, date_value: Optional[datetime]) -> str:
        """Get formatted date.

        Args:
            date_value: Datetime to format

        Returns:
            Formatted date string or empty string
        """
        if not date_value:
            return ""
        return date_value.strftime("%Y-%m-%d")

    def format_created_date(self) -> str:
        """Get formatted creation date.

        Returns:
            Formatted creation date string
        """
        return self.format_date(self.created_at)

    def format_updated_date(self) -> str:
        """Get formatted update date.

        Returns:
            Formatted update date string
        """
        return self.format_date(self.updated_at)

    def format_owner(self) -> str:
        """Get formatted owner string.

        Returns:
            Owner name or "No owner"
        """
        return self.owner.name if self.owner else "No owner"


# Import User for forward reference
from linear.models.users import User  # noqa: E402

Roadmap.model_rebuild()


class RoadmapConnection(BaseModel):
    """Paginated roadmap list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Roadmap] = Field(default_factory=list)
    page_info: PageInfo = Field(alias="pageInfo")
