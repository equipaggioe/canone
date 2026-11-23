"""Sign in with a passkey: the challenge and the assertion."""

import json
import secrets
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Any

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn import verify_authentication_response
from webauthn.helpers import (
    base64url_to_bytes,
    bytes_to_base64url,
    parse_authenticator_data,
    parse_cbor,
)
from webauthn.helpers.exceptions import WebAuthnException

from app import store
from app.config import settings
from app.enums import EventLevel
from app.errors import KeptError
from app.models.account.account import Account
from app.models.account.passkey import Passkey
from app.models.event.event_log import EventLog
from app.schemas.auth import PasskeyCredential, PasskeyOptions
from app.services import authenticators, events
from app.services.authenticators import WAIT_FROM
from app.services.sessions import Client

CHALLENGE_LIFETIME = timedelta(minutes=10)


class Refused(Exception):
    """A check of the assertion that failed, and why."""

    def __init__(self, reason: str, **details: object) -> None:
        """Keep the reason and what the event adds."""
        super().__init__(reason)
        self.details = {"reason": reason, **details}


def origins() -> list[str]:
    """Return the origins of a ceremony: the web and the apps."""
    hosts = (settings.domain, f"app.{settings.domain}", f"panel.{settings.domain}")
    return [f"https://{host}" for host in hosts] + settings.app_origins


def challenge_key(challenge: bytes) -> str:
    """Name the challenge in Valkey."""
    return f"passkey:challenge:{bytes_to_base64url(challenge)}"


async def options() -> PasskeyOptions:
    """Make the options of a login: a challenge, and no passkey."""
    challenge = secrets.token_bytes(16)
    await store.client.set(challenge_key(challenge), b"", ex=CHALLENGE_LIFETIME)
    return PasskeyOptions(
        challenge=bytes_to_base64url(challenge),
        rp_id=settings.domain,
        allow_credentials=[],
        user_verification="preferred",
    )


def event(
    action: str,
    level: EventLevel,
    client: Client,
    passkey: Passkey | None = None,
    details: dict[str, object] | None = None,
) -> EventLog:
    """Build the event of a login with a passkey."""
    return events.event(
        action,
        level,
        actor_id=passkey.account_id if passkey else None,
        target_type="passkey",
        target_id=str(passkey.id) if passkey else None,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
        details=details,
    )


def refuse(session: AsyncSession, client: Client, reason: str) -> KeptError:
    """Answer 401 to a login without a passkey to blame, and log it."""
    session.add(event("authn_login_fail", EventLevel.WARN, client, details={"reason": reason}))
    return KeptError(HTTPException(HTTPStatus.UNAUTHORIZED))


def client_data(credential: PasskeyCredential) -> dict[str, Any]:
    """Read clientDataJSON: the library ignores topOrigin."""
    try:
        data = json.loads(base64url_to_bytes(credential.response.client_data_json))
    except ValueError as error:
        raise Refused("client_data") from error
    if not isinstance(data, dict):
        raise Refused("client_data")
    return data


async def take_challenge(data: dict[str, Any]) -> bytes | None:
    """Delete the challenge, and return it if it lived."""
    try:
        challenge = base64url_to_bytes(str(data.get("challenge", "")))
    except ValueError:
        return None
    if await store.client.getdel(challenge_key(challenge)) is None:
        return None
    return challenge


async def find(
    session: AsyncSession, credential: PasskeyCredential
) -> tuple[Passkey, Account] | None:
    """Find the passkey of the credential ID and lock it."""
    try:
        credential_id = base64url_to_bytes(credential.raw_id)
    except ValueError:
        return None
    query = (
        sa.select(Passkey, Account)
        .join(Account, Account.id == Passkey.account_id)
        .where(Passkey.credential_id == credential_id)
        .with_for_update(of=Passkey)
    )
    return (await session.execute(query)).one_or_none()


def check_client(credential: PasskeyCredential, data: dict[str, Any]) -> None:
    """Refuse what the library does not look at in the client."""
    if credential.client_extension_results:
        raise Refused("client_extensions")
    if data.get("crossOrigin") is True or "topOrigin" in data:
        raise Refused("cross_origin")


def check_authenticator(credential: PasskeyCredential, passkey: Passkey, account: Account) -> None:
    """Refuse what the library does not look at in the authenticator."""
    try:
        auth_data = parse_authenticator_data(
            base64url_to_bytes(credential.response.authenticator_data)
        )
        extensions = parse_cbor(auth_data.extensions) if auth_data.extensions is not None else {}
    except (ValueError, WebAuthnException) as error:
        raise Refused("authenticator_data") from error
    if auth_data.extensions is not None:
        names = sorted(str(name) for name in extensions) if isinstance(extensions, dict) else []
        raise Refused("extensions", extensions=names)
    if auth_data.flags.be != passkey.backup_eligible:
        raise Refused("backup_eligible")
    handle = credential.response.user_handle
    try:
        presented = base64url_to_bytes(handle) if handle is not None else None
    except ValueError as error:
        raise Refused("user_handle") from error
    if presented != account.user_handle:
        raise Refused("user_handle")


def verify(credential: PasskeyCredential, challenge: bytes, passkey: Passkey) -> tuple[int, bool]:
    """Check the signature and the sign count; return the new ones.

    The library compares the sign count before the signature, so it
    gets none: a forged assertion does not report a clone.
    """
    try:
        verified = verify_authentication_response(
            credential=credential.model_dump(mode="json", by_alias=True),
            expected_challenge=challenge,
            expected_rp_id=settings.domain,
            expected_origin=origins(),
            credential_public_key=passkey.public_key,
            credential_current_sign_count=0,
        )
    except (ValueError, WebAuthnException) as error:
        raise Refused("assertion") from error
    new = verified.new_sign_count
    if (new != 0 or passkey.sign_count != 0) and new <= passkey.sign_count:
        # The passkey may be cloned.
        raise Refused("sign_count", stored=passkey.sign_count, presented=new)
    return new, verified.credential_backed_up


async def check(session: AsyncSession, credential: PasskeyCredential, client: Client) -> Account:
    """Return the account of a valid assertion, or answer 401.

    The challenge goes on its first use. A failure that blames a passkey
    counts against it, and stays with its event.
    """
    try:
        data = client_data(credential)
    except Refused as refused:
        raise refuse(session, client, str(refused)) from refused
    challenge = await take_challenge(data)
    if challenge is None:
        raise refuse(session, client, "challenge")
    found = await find(session, credential)
    if found is None:
        raise refuse(session, client, "credential")
    passkey, account = found
    now = datetime.now(UTC)
    early = event(
        "authn_login_fail_max", EventLevel.WARN, client, passkey, {"maxlimit": WAIT_FROM}
    )
    await authenticators.admit(passkey, now, early)
    try:
        check_client(credential, data)
        check_authenticator(credential, passkey, account)
        sign_count, backed_up = verify(credential, challenge, passkey)
    except Refused as refused:
        disabled = authenticators.fail(passkey, now)
        session.add(event("authn_login_fail", EventLevel.WARN, client, passkey, refused.details))
        if disabled:
            session.add(
                event("authn_login_lock", EventLevel.WARN, client, passkey, {"reason": "failures"})
            )
        raise KeptError(HTTPException(HTTPStatus.UNAUTHORIZED)) from refused
    passkey.sign_count = sign_count
    passkey.backup_state = backed_up
    passkey.last_used_at = now
    retries = authenticators.succeed(passkey)
    if retries:
        session.add(
            event(
                "authn_login_successafterfail",
                EventLevel.INFO,
                client,
                passkey,
                {"retries": retries},
            )
        )
    else:
        session.add(event("authn_login_success", EventLevel.INFO, client, passkey))
    return account
