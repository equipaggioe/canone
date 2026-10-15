"""A page of a list, by page token and, to show page numbers, skip."""

import json
from collections.abc import Mapping
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from fastapi.exceptions import RequestValidationError
from pydantic import Field, TypeAdapter, ValidationError, field_validator

from app.config import settings
from app.schemas.base import InputSchema, Schema

JSON: TypeAdapter[Any] = TypeAdapter(Any)


class PageParams(InputSchema):
    """The query parameters of a paged list."""

    page_size: int = Field(50, ge=0)
    page_token: str = ""

    @field_validator("page_size")
    @classmethod
    def fit_page_size(cls, size: int) -> int:
        """Read 0 as the default, and cut a larger size to 100."""
        return min(size or 50, 100)


class SkipParams(PageParams):
    """The query parameters of a list that shows page numbers."""

    page_size: int = Field(50, ge=0, le=100)
    skip: int = Field(0, ge=0)


class Page[T](Schema):
    """One page of a list; the last one has an empty next token."""

    items: list[T]
    next_page_token: str


class CountedPage[T](Page[T]):
    """One page of a list that shows page numbers, with its total."""

    total_size: int


def encode_token(position: object, filters: Mapping[str, Any]) -> str:
    """Encrypt the last position and the filters."""
    content = {"position": position, "filters": filters}
    text = json.dumps(JSON.dump_python(content, mode="json"), separators=(",", ":"))
    return Fernet(settings.page_token_key).encrypt(text.encode()).decode()


def decode_token[T](token: str, filters: Mapping[str, Any], position: type[T]) -> T:
    """Decrypt a position, or answer 422 on a bad page token."""
    try:
        content = json.loads(Fernet(settings.page_token_key).decrypt(token))
        if content["filters"] != JSON.dump_python(filters, mode="json"):
            raise ValueError
        return TypeAdapter(position).validate_python(content["position"])
    except (InvalidToken, ValueError, KeyError, TypeError, ValidationError) as error:
        raise RequestValidationError(
            [{"loc": ("query", "pageToken"), "msg": "Invalid page token", "type": "value_error"}]
        ) from error
