"""An account, identified by its email or its phone."""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

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
    created_at: Mapped[CreatedAt]
