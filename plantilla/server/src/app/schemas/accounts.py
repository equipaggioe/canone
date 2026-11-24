"""The accounts that a superadmin manages."""

from uuid import UUID

from app.enums import Role
from app.schemas.auth import Email, Phone
from app.schemas.base import InputSchema, Schema, Timestamp
from app.schemas.page import PageParams


class AccountSummary(Schema):
    """An account in the list of a superadmin."""

    id: UUID
    email: str | None
    phone: str | None
    role: Role
    created_at: Timestamp
    disabled_at: Timestamp | None


class AccountFilter(PageParams):
    """A page of the accounts, by an exact email or phone if given."""

    email: Email | None = None
    phone: Phone | None = None


class EmailSet(InputSchema):
    """The email a superadmin gives an account: one the holder has."""

    email: Email


class PhoneSet(InputSchema):
    """The phone a superadmin gives an account: one the holder has."""

    phone: Phone
