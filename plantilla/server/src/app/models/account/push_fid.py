"""The installation of an app that receives the pushes of a session."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PushFid(Base):
    """The Firebase installation of a session, and its language."""

    __tablename__ = "push_fid"

    session_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account_session.id", ondelete="CASCADE"), primary_key=True)
    fid: Mapped[str] = mapped_column(unique=True)
    language: Mapped[str]
