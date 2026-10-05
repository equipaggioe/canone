"""The parents of every schema: camelCase, and no extra input."""

from pydantic import BaseModel, ConfigDict
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
