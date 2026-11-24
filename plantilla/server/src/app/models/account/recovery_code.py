"""The saved recovery code of an account."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.account.throttled import Throttled
from app.models.base import Base, CreatedAt


class RecoveryCode(Throttled, Base):
    """The Argon2id hash of the saved code; at most one per account."""

    __tablename__ = "recovery_code"

    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    hash: Mapped[str]
    created_at: Mapped[CreatedAt]
