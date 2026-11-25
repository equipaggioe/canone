"""The messages of the WebSocket.

A message of the client is in CLIENT, by its type; one of the server, in
SERVER. Both go in the components of the OpenAPI.
"""

from typing import Literal

from app.errors import FieldError, Problem
from app.schemas.base import InputSchema, Schema


class AccessTokenData(InputSchema):
    """The access token of a session that its app refreshed."""

    access_token: str


class AccessTokenMessage(InputSchema):
    """An app presents its new access token on its connection."""

    type: Literal["access_token"]
    data: AccessTokenData


# ADR-0237: openapi-generator merges a union of problems into one class
# that requires the errors.
class MessageProblem(Problem):
    """The problem of a message, with its errors if it has fields."""

    errors: list[FieldError] | None = None


class ErrorMessage(Schema):
    """Why the server did not take a message."""

    type: Literal["error"] = "error"
    data: MessageProblem


CLIENT: dict[str, type[InputSchema]] = {"access_token": AccessTokenMessage}
SERVER: list[type[Schema]] = [ErrorMessage]
