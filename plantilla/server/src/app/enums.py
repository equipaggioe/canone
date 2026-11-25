"""The enums of the app."""

from enum import StrEnum


class EventLevel(StrEnum):
    """The level that the OWASP vocabulary gives each event."""

    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class Role(StrEnum):
    """What an account may do.

    The superadmin owns the product (autenticacion.md,
    «Superadministrador»).
    """

    SUPERADMIN = "superadmin"
    USER = "user"


class Method(StrEnum):
    """A way to sign in that a product may offer."""

    PASSKEY = "passkey"
    PASSWORD = "password"
    SMS = "sms"


class Push(StrEnum):
    """A service that a product may send a push through."""

    FCM = "fcm"
    WEB = "web"


class Address(StrEnum):
    """Where a code of the account goes: its email or its phone."""

    EMAIL = "email"
    PHONE = "phone"


class Credential(StrEnum):
    """What a failed attempt presented: an authenticator or a code."""

    PASSWORD = "password"
    PASSKEY = "passkey"
    SMS_CODE = "sms_code"
    EMAIL_RECOVERY = "email_recovery"
    PHONE_RECOVERY = "phone_recovery"
    SAVED_CODE = "saved_code"
    REFRESH_TOKEN = "refresh_token"


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
