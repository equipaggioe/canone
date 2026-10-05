"""The two ways to page a list: by cursor and by page number."""

import base64
import binascii
import json
from collections.abc import Mapping
from typing import Any

from fastapi.exceptions import RequestValidationError
from pydantic import Field, TypeAdapter, ValidationError

from app.schemas.base import InputSchema, Schema

JSON: TypeAdapter[Any] = TypeAdapter(Any)


class CursorParams(InputSchema):
    """The query parameters of a list paged by cursor."""

    limit: int = Field(50, ge=1, le=100)
    cursor: str | None = None


class CursorPage[T](Schema):
    """One page of a list; the last one has no next cursor."""

    items: list[T]
    next_cursor: str | None


class NumberedParams(InputSchema):
    """The query parameters of a list with page numbers."""

    limit: int = Field(50, ge=1, le=100)
    page: int = Field(1, ge=1)

    @property
    def offset(self) -> int:
        """Count the rows before this page."""
        return (self.page - 1) * self.limit


class NumberedPage[T](Schema):
    """One numbered page of a list, with the size of the whole list."""

    items: list[T]
    total: int


def encode_cursor(position: object, filters: Mapping[str, Any]) -> str:
    """Pack the last position and the filters in base64url."""
    content = {"position": position, "filters": filters}
    text = json.dumps(JSON.dump_python(content, mode="json"), separators=(",", ":"))
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def decode_cursor[T](cursor: str, filters: Mapping[str, Any], position: type[T]) -> T:
    """Unpack a position, or answer 422 on a bad cursor."""
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        content = json.loads(base64.urlsafe_b64decode(padded))
        if content["filters"] != JSON.dump_python(filters, mode="json"):
            raise ValueError
        return TypeAdapter(position).validate_python(content["position"])
    except (binascii.Error, ValueError, KeyError, TypeError, ValidationError) as error:
        raise RequestValidationError(
            [{"loc": ("query", "cursor"), "msg": "Invalid cursor", "type": "value_error"}]
        ) from error
