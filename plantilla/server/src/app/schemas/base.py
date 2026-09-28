"""Base schemas: camelCase, cursor pages and RFC 9457 problems."""

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Schema(BaseModel):
    """Every schema inherits from this one."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        from_attributes=True,
    )


class InputSchema(Schema):
    """A request body or a set of query parameters."""

    model_config = ConfigDict(extra="forbid", from_attributes=False)


class PageParams(InputSchema):
    """The query parameters of a paginated list."""

    limit: int = Field(50, ge=1, le=200)
    cursor: str | None = None


class Page[T](Schema):
    """One page of a list."""

    items: list[T]
    next_cursor: str | None


class FieldError(Schema):
    """One invalid field or parameter."""

    detail: str
    pointer: str | None = None
    parameter: str | None = None


class Problem(Schema):
    """An RFC 9457 problem details object."""

    type: str
    title: str
    status: int
    detail: str | None = None
    errors: list[FieldError] | None = None
    trace_id: str
