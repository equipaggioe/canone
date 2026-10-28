"""The events of the OWASP vocabulary, row changes included."""

from datetime import datetime
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import EventLevel
from app.models.base import Base, BigIntPk


class Xid8(sa.types.UserDefinedType[int]):
    """The id of a transaction, which does not wrap around."""

    cache_ok = True

    def get_col_spec(self, **kw: Any) -> str:
        """Name the type in the DDL."""
        return "xid8"


class EventLog(Base):
    """One event; the server only inserts and reads them."""

    __tablename__ = "event_log"
    __table_args__ = (
        # The health route reads the last critical event.
        sa.Index("ix_event_log_critical", "occurred_at", postgresql_where=sa.text("level = 'critical'")),
        # The event log route pages by transaction.
        sa.Index("ix_event_log_xid", "xid", "id"),
    )

    id: Mapped[BigIntPk]
    # ADR-0100: the transaction that wrote it; a row that commits late
    # has a lower one than the rows already read.
    xid: Mapped[int] = mapped_column(Xid8, server_default=sa.text("pg_current_xact_id()"))
    occurred_at: Mapped[datetime] = mapped_column(server_default=sa.text("now()"), index=True)
    action: Mapped[str]
    level: Mapped[EventLevel]
    # No foreign key: the trail outlives the account.
    actor_id: Mapped[UUID | None]
    actor_label: Mapped[str | None]
    target_type: Mapped[str | None]
    target_id: Mapped[str | None]
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None]
    trace_id: Mapped[str]
    details: Mapped[dict[str, Any]] = mapped_column(server_default=sa.text("'{}'::jsonb"))
