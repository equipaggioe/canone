"""The password of an account, and its consecutive failures."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAt


class Password(Base):
    """The Argon2id hash of a password; at most one per account."""

    __tablename__ = "password"

    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    hash: Mapped[str]
    failures: Mapped[int] = mapped_column(server_default=sa.text("0"))
    # The earliest time of the next attempt, from the fifth failure.
    retry_at: Mapped[datetime | None]
    disabled_at: Mapped[datetime | None]
    created_at: Mapped[CreatedAt]
    changed_at: Mapped[datetime] = mapped_column(server_default=sa.text("now()"))
