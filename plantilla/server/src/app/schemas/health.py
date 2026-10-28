"""What the health routes tell whoever monitors the server."""

from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID

from app.enums import EventLevel
from app.schemas.base import Schema, Timestamp


class HealthEvents(Schema):
    """The last events, the last good backup and the disk."""

    last_event_at: Timestamp | None
    last_critical_at: Timestamp | None
    last_backup_at: Timestamp | None
    disk_free_bytes: int
    disk_total_bytes: int


class LoggedEvent(Schema):
    """One row of event_log, as the server wrote it."""

    id: int
    occurred_at: Timestamp
    action: str
    level: EventLevel
    actor_id: UUID | None
    actor_label: str | None
    target_type: str | None
    target_id: str | None
    ip_address: IPv4Address | IPv6Address | None
    user_agent: str | None
    trace_id: str
    details: dict[str, Any]
