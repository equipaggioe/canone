"""The 6-digit codes that verify an email or a phone, in Valkey."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from functools import partial
from html import escape
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import store
from app.config import settings
from app.services import clients, limits, messages
from app.services.limits import Rule
from app.services.sessions import Client
from app.translations import catalog

LIFETIME = timedelta(minutes=10)
# The third failed attempt invalidates the code.
ATTEMPTS = 3
MINUTE, HOUR, DAY = timedelta(minutes=1), timedelta(hours=1), timedelta(days=1)
# The tenth 404 to the codes asked by an IP in 15 minutes blocks it 30
# minutes: the code to sign in and the code to recover count together.
UNKNOWN = 10
UNKNOWN_WINDOW = timedelta(minutes=15)
BLOCK = timedelta(minutes=30)


def block_key(client: Client) -> str:
    """Name the block of the codes of an IP."""
    return f"code:{client.ip_address}"


async def check_open(client: Client) -> None:
    """Answer 429 to an IP blocked by its 404 answers."""
    await limits.check_block(block_key(client), "Too many codes asked for unknown accounts")


async def unknown(client: Client) -> HTTPException:
    """Count a 404 of an IP, blocking it on the tenth, and return it."""
    rule = Rule(f"code:unknown:{client.ip_address}", UNKNOWN, UNKNOWN_WINDOW, "")
    if await limits.hit(rule):
        await limits.block(block_key(client), BLOCK)
    return HTTPException(HTTPStatus.NOT_FOUND, "No account has it")


def key(purpose: str, address: str) -> str:
    """Name the code of an address in Valkey."""
    return f"code:{purpose}:{hashlib.sha256(address.encode()).hexdigest()}"


def digest(code: str) -> bytes:
    """Hash a code: whoever reads Valkey does not read it."""
    return hashlib.sha256(code.encode()).digest()


async def issue(purpose: str, address: str) -> str:
    """Make a code for an address; it replaces the previous one."""
    code = f"{secrets.randbelow(10**6):06d}"
    name = key(purpose, address)
    async with store.client.pipeline(transaction=True) as pipe:
        pipe.set(name, digest(code), px=limits.milliseconds(LIFETIME))
        pipe.delete(f"{name}:attempts")
        await pipe.execute()
    return code


async def take(purpose: str, address: str, code: str) -> bool:
    """Tell whether a code is the live one, and spend it.

    Each attempt counts before the comparison, so a code is compared at
    most three times, and only one attempt deletes it.
    """
    name = key(purpose, address)
    attempts = await store.client.incr(f"{name}:attempts")
    if attempts == 1:
        await store.client.pexpire(f"{name}:attempts", limits.milliseconds(LIFETIME))
    stored = await store.client.get(name)
    if stored is None or attempts > ATTEMPTS:
        return False
    if hmac.compare_digest(stored, digest(code)):
        return bool(await store.client.delete(name))
    if attempts == ATTEMPTS:
        await store.client.delete(name)
    return False


def email_rules(email: str) -> list[Rule]:
    """One code a minute to an email, and five an hour."""
    subject = hashlib.sha256(email.encode()).hexdigest()
    return [
        Rule(f"code:email:minute:{subject}", 1, MINUTE, "One code a minute to this email"),
        Rule(f"code:email:hour:{subject}", 5, HOUR, "Five codes an hour to this email"),
    ]


def sms_rules(phone: str, client: Client) -> list[Rule]:
    """One SMS a minute, five an hour and ten a day to a number.

    An IP asks for ten an hour.
    """
    subject = hashlib.sha256(phone.encode()).hexdigest()
    return [
        Rule(f"code:sms:minute:{subject}", 1, MINUTE, "One SMS a minute to this number"),
        Rule(f"code:sms:hour:{subject}", 5, HOUR, "Five SMS an hour to this number"),
        Rule(f"code:sms:day:{subject}", 10, DAY, "Ten SMS a day to this number"),
        Rule(f"code:sms:ip:{client.ip_address}", 10, HOUR, "Ten SMS an hour from this address"),
    ]


def send_email(session: AsyncSession, email: str, code: str, language: str) -> None:
    """Send a code by email once the request commits."""
    t = catalog(language).gettext
    text = t("Your code is {code}. It lasts 10 minutes.").format(code=code)
    expires = datetime.now(UTC) + LIFETIME
    send = partial(messages.email, email, t("Your code"), text, f"<p>{escape(text)}</p>", expires)
    messages.later(session, send)


def sms_text(code: str, language: str, host: str, piece: str) -> str:
    """Write the SMS of a code.

    An Android app finds its hash in the second last line, and the last
    one binds the code to the host of the web where it is written: the
    surface the request came to.
    """
    if host not in clients.surfaces():
        raise HTTPException(HTTPStatus.BAD_REQUEST, "The host is not a surface of the domain")
    lines = [catalog(language).gettext("Your code is {code}.").format(code=code)]
    if piece in settings.sms_hashes:
        lines.append(settings.sms_hashes[piece])
    lines.append(f"@{host} #{code}")
    return "\n".join(lines)


def send_sms(session: AsyncSession, phone: str, text: str) -> None:
    """Send the SMS of a code once the request commits."""
    messages.later(session, partial(messages.sms, phone, text, datetime.now(UTC) + LIFETIME))
