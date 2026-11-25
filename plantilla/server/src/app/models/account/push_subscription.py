"""The browser that receives the pushes of a session."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PushSubscription(Base):
    """The Web Push subscription of a session, and its language."""

    __tablename__ = "push_subscription"

    session_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account_session.id", ondelete="CASCADE"), primary_key=True)
    # Whoever has it sends to the browser: it goes in no log.
    endpoint: Mapped[str] = mapped_column(unique=True)
    p256dh: Mapped[str]
    auth: Mapped[str]
    language: Mapped[str]
