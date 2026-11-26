"""The notices to the holder of an account, to every address."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from functools import partial
from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.account.account import Account
from app.services import messages, push
from app.services.fcm import Content
from app.translations import catalog

# fastapi.md, «Push»: the lifetime of a notice that does not expire.
LIFETIME = timedelta(days=28)
# autenticacion.md: what a push opens, and its channel of Android.
PAGE = "/account"
CHANNEL = "security"


class Notice(StrEnum):
    """What a notice tells the holder."""

    PASSKEY_LINKED = "passkey_linked"
    PASSKEY_DELETED = "passkey_deleted"
    PASSKEY_CLONED = "passkey_cloned"
    PASSKEY_ENABLED = "passkey_enabled"
    PHONE_ENABLED = "phone_enabled"
    PASSWORD_ADDED = "password_added"
    PASSWORD_CHANGED = "password_changed"
    EMAIL_CHANGED = "email_changed"
    PHONE_CHANGED = "phone_changed"
    RECOVERY_CODE_CREATED = "recovery_code_created"
    RECOVERY_PENDING = "recovery_pending"
    RECOVERED = "recovered"
    ACCOUNT_DISABLED = "account_disabled"
    ACCOUNT_DELETED = "account_deleted"
    ACCOUNT_CREATED = "account_created"
    ROLE_CHANGED = "role_changed"


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
    Notice.PASSKEY_ENABLED: (
        "A passkey of your account was enabled again",
        "The passkey {name} of your account was enabled again. If you did not enable it, "
        "delete it in the app and write to {contact}.",
    ),
    Notice.PHONE_ENABLED: (
        "The phone of your account was enabled again",
        "The phone of your account signs in with its code again. If you did not enable it, "
        "change the phone in the app and write to {contact}.",
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
    Notice.ACCOUNT_DISABLED: (
        "Your account was disabled",
        "An administrator disabled your account: its passkeys, its password and its sessions "
        "were deleted. Write to {contact} to know why.",
    ),
    Notice.ACCOUNT_DELETED: (
        "Your account was deleted",
        "Your account was deleted. If you did not delete it, write to {contact}.",
    ),
    Notice.ACCOUNT_CREATED: (
        "An account was created for you",
        "An administrator created an account for you with this address. To sign in the first "
        "time, recover it in the app with a code sent here. If you did not expect it, write to "
        "{contact}.",
    ),
    Notice.ROLE_CHANGED: (
        "The role of your account changed",
        "An administrator changed what your account may do. If you did not expect it, write to "
        "{contact}.",
    ),
}


def content(language: str, notice: Notice, name: str) -> Content:
    """Write a notice in a language, as its push."""
    t = catalog(language).gettext
    subject, body = TEXTS[notice]
    text = t(body).format(name=name, contact=settings.contact)
    return Content(t(subject), text, PAGE, CHANNEL, LIFETIME)


async def notify(
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
    written = content(account.language, notice, name)
    text = written.body
    expires = datetime.now(UTC) + LIFETIME
    addresses = {account.email, account.phone, previous} - {None}
    for address in sorted(address for address in addresses if address is not None):
        if address.startswith("+"):
            messages.later(session, partial(messages.sms, address, text, expires))
        else:
            html = f"<p>{escape(text)}</p>"
            send = partial(messages.email, address, written.title, text, html, expires)
            messages.later(session, send)
    await push.later(session, account.id, partial(content, notice=notice, name=name))
