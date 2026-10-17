"""The parents of every schema: camelCase, and no extra input."""

import re
from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel

RFC3339 = re.compile(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})")


def check_rfc3339(value: object) -> object:
    """Let through a datetime, or a string written as RFC 3339."""
    if isinstance(value, datetime) or (isinstance(value, str) and RFC3339.fullmatch(value)):
        return value
    raise ValueError("expected an RFC 3339 date and time")


def to_utc(moment: datetime) -> datetime:
    """Move a datetime to UTC."""
    return moment.astimezone(UTC)


Timestamp = Annotated[AwareDatetime, BeforeValidator(check_rfc3339), AfterValidator(to_utc)]
"""Every date and time of a schema."""


class Schema(BaseModel):
    """Every schema inherits from this one.

    It reads a row or the code by field name, created_at, and writes
    JSON by alias, createdAt.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
        validate_by_name=True,
        from_attributes=True,
    )


class InputSchema(Schema):
    """A request body or a set of query parameters, read by alias."""

    model_config = ConfigDict(extra="forbid", from_attributes=False, validate_by_name=False)
