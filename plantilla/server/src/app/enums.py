"""The enums of the app."""

from enum import StrEnum


class EventLevel(StrEnum):
    """The level that the OWASP vocabulary gives each event."""

    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"
