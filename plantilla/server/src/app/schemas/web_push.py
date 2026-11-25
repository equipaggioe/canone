"""The subscription of a browser, as toJSON() writes it, and its key."""

import base64
from typing import Annotated
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.asymmetric import ec
from pydantic import AfterValidator, Field, StringConstraints

from app.schemas.base import InputSchema, Schema

AUTH_BYTES = 16


def check_endpoint(value: str) -> str:
    """Require the host of an endpoint, and a port if it has one."""
    parts = urlsplit(value)
    if not parts.hostname or parts.port == 0:
        raise ValueError("expected an https URL")
    return value


def decode(value: str) -> bytes:
    """Read base64url without padding."""
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def check_point(value: str) -> str:
    """Require an uncompressed point of P-256."""
    point = decode(value)
    if len(point) != 65:
        raise ValueError("expected an uncompressed point of P-256")
    ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), point)
    return value


def check_auth(value: str) -> str:
    """Require the 16 bytes of an authentication secret."""
    if len(decode(value)) != AUTH_BYTES:
        raise ValueError("expected 16 bytes")
    return value


Base64Url = Annotated[str, StringConstraints(pattern="^[A-Za-z0-9_-]+$", max_length=128)]
# An index of PostgreSQL takes the 2048 characters, which are ASCII.
Endpoint = Annotated[
    str,
    StringConstraints(pattern="^https://[!-~]+$", max_length=2048),
    AfterValidator(check_endpoint),
]


class SubscriptionKeys(InputSchema):
    """The keys that encrypt a push for the browser."""

    p256dh: Annotated[Base64Url, AfterValidator(check_point)] = Field(alias="p256dh")
    auth: Annotated[Base64Url, AfterValidator(check_auth)]


class SubscriptionRegistration(InputSchema):
    """The subscription of the browser of the session."""

    endpoint: Endpoint
    # One that expires answers 404 or 410 when it is sent to.
    expiration_time: float | None = None
    keys: SubscriptionKeys


class PushKey(Schema):
    """The public key of VAPID, the applicationServerKey."""

    key: str
