"""Attachment-related Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from linear.models.base import PageInfo


class Attachment(BaseModel):
    """Represents an issue attachment."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    url: HttpUrl
    created_at: datetime = Field(alias="createdAt")
    subtitle: str | None = None
    source: str | None = None  # URL source
    source_type: str | None = Field(None, alias="sourceType")
    metadata: dict | None = None


class AttachmentConnection(BaseModel):
    """Paginated attachment list from GraphQL."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[Attachment] = Field(default_factory=list)
    page_info: PageInfo = Field(default_factory=PageInfo, alias="pageInfo")
