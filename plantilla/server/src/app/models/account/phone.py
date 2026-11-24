"""The phone of an account, as the authenticator of the SMS code."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.account.throttled import Throttled
from app.models.base import Base, CreatedAt


class Phone(Throttled, Base):
    """The failures of the codes to a phone; account has the number."""

    __tablename__ = "phone"

    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[CreatedAt]
    changed_at: Mapped[datetime] = mapped_column(server_default=sa.text("now()"))
