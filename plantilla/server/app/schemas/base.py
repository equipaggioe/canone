from datetime import datetime
from typing import Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic.alias_generators import to_camel

from app.core.enums import ErrorCode

T = TypeVar("T")


# Base Pydantic configurations
class SchemaBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
        ser_json_bytes="base64",
    )


class SchemaInputBase(SchemaBase):
    model_config = ConfigDict(
        from_attributes=False,
        extra="forbid",
        ser_json_bytes="base64",
    )


class QueryParamsBase(SchemaBase):
    model_config = ConfigDict(
        from_attributes=False,
    )


# Response structures (Response Wrappers)
class PaginationParams(QueryParamsBase):
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(50, ge=1, le=200, description="Items per page")
    sort: str | None = Field(None, description="Sort field")
    order: Literal["asc", "desc"] = Field("desc", description="Sort order")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class PageMeta(SchemaBase):
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total items available")

    @computed_field
    @property
    def total_pages(self) -> int:
        return (self.total + self.per_page - 1) // self.per_page

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        return self.page > 1


class PageResponse(SchemaBase, Generic[T]):
    items: list[T] = Field(description="List of items for the current page")
    meta: PageMeta = Field(description="Pagination metadata")


class ErrorResponse(SchemaBase):
    status: int = Field(ge=400, le=599, description="HTTP error code")
    detail: str = Field(description="Specific detail of this occurrence")
    error_code: ErrorCode = Field(description="Business error code")
    errors: dict[str, list[str]] | None = Field(None, description="Field validation errors")
    request_id: str | None = Field(None, description="Request identifier")


class EnumOption(SchemaBase):
    value: str = Field(description="Raw enum value")
    label: str = Field(description="Human-readable label for the enum value")


# Geographic domain models
class Point(SchemaBase):
    lat: float = Field(..., description="Latitude in decimal degrees", ge=-90, le=90)
    lng: float = Field(..., description="Longitude in decimal degrees", ge=-180, le=180)


class Waypoint(Point):
    stop_id: int | None = Field(None, description="Optional stop identifier")
    order: int | None = Field(None, description="Order of the waypoint in the sequence")
