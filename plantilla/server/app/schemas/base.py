from datetime import datetime
from typing import Any, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic.alias_generators import to_camel

from app.core.enums import ProblemType

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


# RFC 9457 problem details, served as application/problem+json
class FieldError(SchemaBase):
    detail: str = Field(description="What is wrong with the field")
    pointer: str = Field(description="JSON Pointer to the field in the request content")


class ProblemDetails(SchemaBase):
    type: ProblemType = Field(description="Problem type URI; the client branches on it")
    title: str = Field(description="Short summary of the problem type")
    status: int = Field(ge=400, le=599, description="Same HTTP status code as the response")
    detail: str = Field(description="Specific detail of this occurrence")
    errors: list[FieldError] | None = Field(None, description="Field validation errors")
    trace_id: str | None = Field(None, description="W3C Trace Context trace-id of the request")


# ADR-0015: FastAPI documents `model` under the route's media type, application/json, so
# application/problem+json points to the same schema by hand. 422 is listed because FastAPI
# would otherwise document its own validation error.
_PROBLEM_RESPONSE: dict[str, Any] = {
    "model": ProblemDetails,
    "content": {
        "application/problem+json": {"schema": {"$ref": "#/components/schemas/ProblemDetails"}}
    },
}
PROBLEM_RESPONSES: dict[int | str, dict[str, Any]] = {
    "4XX": _PROBLEM_RESPONSE,
    422: _PROBLEM_RESPONSE,
    "5XX": _PROBLEM_RESPONSE,
}


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
