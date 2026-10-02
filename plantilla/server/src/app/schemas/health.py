"""The answer of the health check."""

from typing import Literal

from app.schemas.base import Schema


class Health(Schema):
    """The server and its database answer."""

    status: Literal["ok"]
