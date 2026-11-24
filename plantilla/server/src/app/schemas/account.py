"""The bodies and responses of the account of the session."""

from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from app.enums import Address, Credential, Role, SessionKind
from app.schemas.auth import Code, Email, PasskeyName, PasskeyRegistration, Phone
from app.schemas.base import InputSchema, Schema, Timestamp


class PasskeyView(Schema):
    """A passkey of the account, by its name and its last use."""

    id: UUID
    name: str
    created_at: Timestamp
    last_used_at: Timestamp | None
    disabled_at: Timestamp | None


class PasswordView(Schema):
    """The password of the account: when it changed, and if disabled."""

    changed_at: Timestamp
    disabled_at: Timestamp | None


class PhoneView(Schema):
    """The phone of the account, as the authenticator of its code."""

    number: str
    changed_at: Timestamp
    disabled_at: Timestamp | None


class AccountView(Schema):
    """The account of the session, and its authenticators."""

    id: UUID
    email: str | None
    phone: PhoneView | None
    role: Role
    created_at: Timestamp
    password: PasswordView | None


class FailureView(Schema):
    """A failed attempt on the account, from where it came."""

    occurred_at: Timestamp
    credential: Credential
    passkey_id: UUID | None
    ip_address: IPv4Address | IPv6Address | None
    user_agent: str | None


class SessionView(Schema):
    """An open session of the account, by its device."""

    id: UUID
    kind: SessionKind
    user_agent: str | None
    created_at: Timestamp
    last_used_at: Timestamp
    current: bool


class RecoveryView(Schema):
    """The pending recovery of the account: its address and its time."""

    address: Address
    applies_at: Timestamp


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
