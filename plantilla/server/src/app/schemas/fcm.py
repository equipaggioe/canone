"""The installation of an app, which FCM sends to."""

from typing import Annotated

from pydantic import StringConstraints

from app.schemas.base import InputSchema


class FidRegistration(InputSchema):
    """The Firebase installation ID of the app of the session."""

    fid: Annotated[str, StringConstraints(pattern="^[A-Za-z0-9_-]{22}$")]
