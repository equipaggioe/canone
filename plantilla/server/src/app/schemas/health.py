"""What the health route tells whoever monitors the server."""

from app.schemas.base import Schema, Timestamp


class HealthEvents(Schema):
    """The last critical event and the last good backup, or null."""

    last_critical_at: Timestamp | None
    last_backup_at: Timestamp | None
