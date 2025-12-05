"""User-related Pydantic models."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from .base import Organization, PageInfo

if TYPE_CHECKING:
    pass


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


class UserConnection(BaseModel):
    """Paginated user list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[User] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
