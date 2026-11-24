"""An account, identified by its email or its phone."""

import secrets

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import Role
from app.models.base import Base, CreatedAt, UuidPk


class Account(Base):
    """Whoever signs in; the email and the phone belong to one."""

    __tablename__ = "account"
    __table_args__ = (sa.CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name="identified"),)

    id: Mapped[UuidPk]
    # Kept in lowercase, as the server receives it.
    email: Mapped[str | None] = mapped_column(unique=True)
    # A + and digits only.
    phone: Mapped[str | None] = mapped_column(unique=True)
    # The user handle of its passkeys: 64 random bytes.
    user_handle: Mapped[bytes] = mapped_column(default=lambda: secrets.token_bytes(64))
    role: Mapped[Role]
    # The language of its notices: the last one it signed in with.
    language: Mapped[str]
    created_at: Mapped[CreatedAt]
