"""A passkey of an account, as WebAuthn registers it."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.models.account.throttled import Throttled
from app.models.base import Base, CreatedAt, UuidPk


class Passkey(Throttled, Base):
    """A discoverable credential; the login finds it by its ID."""

    __tablename__ = "passkey"

    id: Mapped[UuidPk]
    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), index=True)
    credential_id: Mapped[bytes] = mapped_column(unique=True)
    # The COSE key of the registration.
    public_key: Mapped[bytes]
    sign_count: Mapped[int] = mapped_column(sa.BigInteger)
    uv_initialized: Mapped[bool]
    # As the client sends them: a new transport is not refused.
    transports: Mapped[list[str]] = mapped_column(ARRAY(TEXT))
    backup_eligible: Mapped[bool]
    backup_state: Mapped[bool]
    name: Mapped[str]
    created_at: Mapped[CreatedAt]
    changed_at: Mapped[datetime] = mapped_column(server_default=sa.text("now()"))
    last_used_at: Mapped[datetime | None]
