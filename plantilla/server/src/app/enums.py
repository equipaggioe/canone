"""The enums of the app."""

from enum import StrEnum


class EventLevel(StrEnum):
    """The level that the OWASP vocabulary gives each event."""

    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class Role(StrEnum):
    """What an account may do; an admin signs in only with a passkey."""

    ADMIN = "admin"
    USER = "user"


class Method(StrEnum):
    """A way to sign in that a product may offer."""

    PASSKEY = "passkey"
    PASSWORD = "password"


class SessionKind(StrEnum):
    """How a session is presented: a cookie, or the tokens of an app."""

    WEB = "web"
    APP = "app"


class TokenErrorCode(StrEnum):
    """The errors of RFC 6749 that the token endpoint answers."""

    INVALID_REQUEST = "invalid_request"
    INVALID_GRANT = "invalid_grant"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"
    INVALID_SCOPE = "invalid_scope"
