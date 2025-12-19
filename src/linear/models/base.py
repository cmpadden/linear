"""Base Pydantic models shared across entities."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class PageInfo(BaseModel):
    """GraphQL pagination info."""

    model_config = ConfigDict(populate_by_name=True)

    has_next_page: bool = Field(default=False, alias="hasNextPage")
    end_cursor: Optional[str] = Field(None, alias="endCursor")
    start_cursor: Optional[str] = Field(None, alias="startCursor")
    has_previous_page: bool = Field(default=False, alias="hasPreviousPage")


T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    """Paginated result with items and pagination metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    page_info: PageInfo
    total_count: Optional[int] = None  # Not always available from API
    current_page: int = 1
    per_page: int = 50


class Organization(BaseModel):
    """Represents a Linear organization."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    url_key: Optional[str] = Field(None, alias="urlKey")
