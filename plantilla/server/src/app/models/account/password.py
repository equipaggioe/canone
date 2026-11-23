"""The password of an account."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.account.throttled import Throttled
from app.models.base import Base, CreatedAt


class Password(Throttled, Base):
    """The Argon2id hash of a password; at most one per account."""

    __tablename__ = "password"

    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    hash: Mapped[str]
    created_at: Mapped[CreatedAt]
    changed_at: Mapped[datetime] = mapped_column(server_default=sa.text("now()"))
