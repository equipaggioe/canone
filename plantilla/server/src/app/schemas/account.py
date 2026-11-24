"""The bodies and responses of the account of the session."""

from uuid import UUID

from app.schemas.auth import Code, Email, PasskeyName, PasskeyRegistration, Phone
from app.schemas.base import InputSchema, Schema, Timestamp


class PasskeyView(Schema):
    """A passkey of the account, by its name and its last use."""

    id: UUID
    name: str
    created_at: Timestamp
    last_used_at: Timestamp | None


class PasskeyLink(InputSchema):
    """A new passkey of the account, and its name."""

    name: PasskeyName
    credential: PasskeyRegistration


class EmailCode(InputSchema):
    """The new email, which receives the code."""

    email: Email


class EmailChange(EmailCode):
    """The new email, and the code it received."""

    code: Code


class PhoneCode(InputSchema):
    """The new phone, which receives the code."""

    phone: Phone


class PhoneChange(PhoneCode):
    """The new phone, and the code it received."""

    code: Code
