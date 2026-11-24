"""Write the events of event_log, and purge the expired ones."""

import ipaddress
from collections.abc import Mapping
from datetime import timedelta
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from app.database import SessionFactory
from app.enums import EventLevel
from app.models.event.event_log import EventLog
from app.tracing import trace_id

# The IP and the user agent are personal data.
RETENTION_DAYS = 365

# The fields whose value a row change keeps, by table: a new column is
# not logged by itself.
LOGGED_FIELDS: dict[str, frozenset[str]] = {"account": frozenset({"role"})}


def event(
    action: str,
    level: EventLevel,
    *,
    actor_id: UUID | None = None,
    actor_label: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> EventLog:
    """Build an event in the current trace.

    A malformed address is left out and named in details: the event is
    kept with the failure.
    """
    kept = dict(details or {})
    address = valid_address(ip_address)
    if ip_address is not None and address is None:
        kept["malformed"] = ["ip_address"]
    return EventLog(
        action=action,
        level=level,
        actor_id=actor_id,
        actor_label=actor_label,
        target_type=target_type,
        target_id=target_id,
        ip_address=address,
        user_agent=user_agent,
        trace_id=trace_id(),
        details=kept,
    )


def valid_address(value: str | None) -> str | None:
    """Return the IP address written by its standard, or none."""
    try:
        return str(ipaddress.ip_address(value)) if value is not None else None
    except ValueError:
        return None


async def record(row: EventLog) -> None:
    """Write an event in its own transaction.

    The event stays if the request rolls back.

    The event of a row change goes instead in the session of the change,
    with session.add, so a change that rolls back leaves no event.
    """
    async with SessionFactory.begin() as session:
        session.add(row)


def changes(table: str, changed: Mapping[str, Any]) -> dict[str, Any]:
    """Keep the value of the listed fields, and the name of the rest."""
    logged = LOGGED_FIELDS.get(table, frozenset())
    return {
        "changed": sorted(changed),
        "values": {name: value for name, value in changed.items() if name in logged},
    }


async def purge() -> None:
    """Delete the events past the retention.

    Only the owner of the schema deletes from event_log: the purge runs
    with the database_url of the migrations.
    """
    expired = EventLog.occurred_at < sa.func.now() - timedelta(days=RETENTION_DAYS)
    async with SessionFactory.begin() as session:
        await session.execute(sa.delete(EventLog).where(expired))
