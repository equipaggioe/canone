"""The failures of the recovery codes to an address of an account."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import Address
from app.models.account.throttled import Throttled
from app.models.base import Base


class RecoveryAddress(Throttled, Base):
    """The email or the phone as a way to recover, by its failures."""

    __tablename__ = "recovery_address"

    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    address: Mapped[Address] = mapped_column(primary_key=True)
