"""A recovery that waits 24 hours, with its new authenticator."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import Address
from app.models.base import Base, CreatedAt

# The new authenticator is a password or a verified passkey, whole.
AUTHENTICATOR = (
    "(password_hash IS NOT NULL AND credential_id IS NULL AND public_key IS NULL AND sign_count IS NULL AND uv_initialized IS NULL AND transports IS NULL AND backup_eligible IS NULL AND backup_state IS NULL AND passkey_name IS NULL)"
    " OR (password_hash IS NULL AND credential_id IS NOT NULL AND public_key IS NOT NULL AND sign_count IS NOT NULL AND uv_initialized IS NOT NULL AND transports IS NOT NULL AND backup_eligible IS NOT NULL AND backup_state IS NOT NULL AND passkey_name IS NOT NULL)"
)


class Recovery(Base):
    """The pending recovery of an account; a new one replaces it."""

    __tablename__ = "recovery"
    __table_args__ = (sa.CheckConstraint(AUTHENTICATOR, name="authenticator"),)

    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    address: Mapped[Address]
    applies_at: Mapped[datetime] = mapped_column(index=True)
    password_hash: Mapped[str | None]
    credential_id: Mapped[bytes | None]
    public_key: Mapped[bytes | None]
    sign_count: Mapped[int | None] = mapped_column(sa.BigInteger)
    uv_initialized: Mapped[bool | None]
    transports: Mapped[list[str] | None] = mapped_column(ARRAY(TEXT))
    backup_eligible: Mapped[bool | None]
    backup_state: Mapped[bool | None]
    passkey_name: Mapped[str | None]
    created_at: Mapped[CreatedAt]
