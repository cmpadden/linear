"""Comment-related Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from linear.models.base import PageInfo


class CommentUser(BaseModel):
    """User information for a comment."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    display_name: str = Field(alias="displayName")
    email: str


class Comment(BaseModel):
    """Represents a Linear comment."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    body: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    edited_at: datetime | None = Field(None, alias="editedAt")
    user: CommentUser

    def format_created_date(self) -> str:
        """Get formatted creation date."""
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    def format_updated_date(self) -> str:
        """Get formatted updated date."""
        return self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else ""


class CommentConnection(BaseModel):
    """Paginated comment list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Comment] = Field(default_factory=list)
    page_info: PageInfo = Field(alias="pageInfo")
