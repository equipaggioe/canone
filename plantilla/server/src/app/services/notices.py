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
    EMAIL_CHANGED = "email_changed"
    PHONE_CHANGED = "phone_changed"


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
    Notice.EMAIL_CHANGED: (
        "The email of your account changed",
        "The email of your account changed. If you did not change it, write to {contact}.",
    ),
    Notice.PHONE_CHANGED: (
        "The phone of your account changed",
        "The phone of your account changed. If you did not change it, write to {contact}.",
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
