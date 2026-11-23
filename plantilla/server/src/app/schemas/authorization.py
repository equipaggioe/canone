"""The answer of the authorization page with its passkey."""

from app.schemas.auth import PasskeyCredential
from app.schemas.base import InputSchema, Schema


class Grant(InputSchema):
    """The waiting request, and the passkey that signs it in."""

    request: str
    credential: PasskeyCredential


class Redirect(Schema):
    """Where the page goes back to the client, with the code."""

    redirect: str
