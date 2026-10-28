"""What the health route tells whoever monitors the server."""

from app.schemas.base import Schema, Timestamp


class HealthEvents(Schema):
    """The last events, the last good backup and the disk."""

    last_event_at: Timestamp | None
    last_critical_at: Timestamp | None
    last_backup_at: Timestamp | None
    disk_free_bytes: int
    disk_total_bytes: int
