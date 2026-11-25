"""The messages of the WebSocket.

A message of the client is in CLIENT, by its type; one of the server, in
SERVER. Both go in the components of the OpenAPI.
"""

from typing import Literal

from app.errors import Problem, ValidationProblem
from app.schemas.base import InputSchema, Schema


class AccessTokenData(InputSchema):
    """The access token of a session that its app refreshed."""

    access_token: str


class AccessTokenMessage(InputSchema):
    """An app presents its new access token on its connection."""

    type: Literal["access_token"]
    data: AccessTokenData


class ErrorMessage(Schema):
    """Why the server did not take a message."""

    type: Literal["error"] = "error"
    data: ValidationProblem | Problem


CLIENT: dict[str, type[InputSchema]] = {"access_token": AccessTokenMessage}
SERVER: list[type[Schema]] = [ErrorMessage]
