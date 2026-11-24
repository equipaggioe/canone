"""The notices to the holder of an account, by email and by SMS."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from functools import partial
from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.account.account import Account
from app.services import messages
from app.translations import catalog

# fastapi.md, «Push»: the lifetime of a notice that does not expire.
LIFETIME = timedelta(days=28)


class Notice(StrEnum):
    """What a notice tells the holder."""

    PASSKEY_LINKED = "passkey_linked"
    PASSKEY_DELETED = "passkey_deleted"
    PASSKEY_CLONED = "passkey_cloned"
    PASSWORD_ADDED = "password_added"
    PASSWORD_CHANGED = "password_changed"
    EMAIL_CHANGED = "email_changed"
    PHONE_CHANGED = "phone_changed"
    RECOVERY_CODE_CREATED = "recovery_code_created"
    RECOVERY_PENDING = "recovery_pending"
    RECOVERED = "recovered"


# Each notice says what happened, what to do and whom to write to, if
# the holder did not do it.
TEXTS = {
    Notice.PASSKEY_LINKED: (
        "A passkey was added to your account",
        "The passkey {name} was added to your account. If you did not add it, "
        "delete it in the app and write to {contact}.",
    ),
    Notice.PASSKEY_DELETED: (
        "A passkey was deleted from your account",
        "The passkey {name} was deleted from your account. If you did not delete it, "
        "review your passkeys in the app and write to {contact}.",
    ),
    Notice.PASSKEY_CLONED: (
        "A passkey of your account may be copied",
        "A sign-in with the passkey {name} was refused: the passkey may be copied. "
        "Delete it in the app, add a new one and write to {contact}.",
    ),
    Notice.PASSWORD_ADDED: (
        "A password was added to your account",
        "A password was added to your account. If you did not add it, "
        "delete your sessions in the app, reset the password and write to {contact}.",
    ),
    Notice.PASSWORD_CHANGED: (
        "The password of your account changed",
        "The password of your account changed. If you did not change it, close your "
        "other sessions in the app, reset the password and write to {contact}.",
    ),
    Notice.EMAIL_CHANGED: (
        "The email of your account changed",
        "The email of your account changed. If you did not change it, write to {contact}.",
    ),
    Notice.PHONE_CHANGED: (
        "The phone of your account changed",
        "The phone of your account changed. If you did not change it, write to {contact}.",
    ),
    Notice.RECOVERY_CODE_CREATED: (
        "A recovery code was created for your account",
        "A new recovery code was created for your account, and the previous one stopped "
        "working. If you did not create it, review your account in the app and write to "
        "{contact}.",
    ),
    Notice.RECOVERY_PENDING: (
        "Your account will be recovered in 24 hours",
        "Someone asked to recover your account with the code sent to your email, and it "
        "applies in 24 hours. If it was not you, sign in or cancel it in the app, and write "
        "to {contact}.",
    ),
    Notice.RECOVERED: (
        "Your account was recovered",
        "Your account was recovered with a code. If you did not do it, sign in, close your "
        "other sessions in the app and write to {contact}.",
    ),
}


def notify(
    session: AsyncSession,
    account: Account,
    notice: Notice,
    *,
    name: str = "",
    previous: str | None = None,
) -> None:
    """Notify every address of the account once the request commits.

    The previous email or phone of a change is notified too.
    """
    t = catalog(account.language).gettext
    subject, body = TEXTS[notice]
    text = t(body).format(name=name, contact=settings.contact)
    expires = datetime.now(UTC) + LIFETIME
    addresses = {account.email, account.phone, previous} - {None}
    for address in sorted(address for address in addresses if address is not None):
        if address.startswith("+"):
            messages.later(session, partial(messages.sms, address, text, expires))
        else:
            html = f"<p>{escape(text)}</p>"
            send = partial(messages.email, address, t(subject), text, html, expires)
            messages.later(session, send)
