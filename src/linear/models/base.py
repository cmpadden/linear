"""Base Pydantic models shared across entities."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
