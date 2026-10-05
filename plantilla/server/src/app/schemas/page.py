"""The request and the response of a paginated list."""

from pydantic import Field

from app.schemas.base import InputSchema, Schema


class PageParams(InputSchema):
    """The query parameters of a paginated list."""

    limit: int = Field(20, ge=1, le=100)
    cursor: str | None = None


class Page[T](Schema):
    """One page of a list; the last one has no next cursor."""

    items: list[T]
    next_cursor: str | None
