"""Signing in with a passkey, against an authenticator of software."""

import hashlib
import json
import secrets
import struct
from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie
from typing import Any

import pytest
import sqlalchemy as sa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

from app import errors, store
from app.config import settings
from app.models.account.account import Account
from app.models.account.passkey import Passkey
from app.models.event.event_log import EventLog
from app.services import events, passkeys, sessions

ORIGIN = f"https://app.{settings.domain}"
UP, UV, BE, BS, ED = 0x01, 0x04, 0x08, 0x10, 0x80


def cbor_bytes(value: bytes) -> bytes:
    """Encode a byte string of up to 255 bytes in CBOR."""
    return bytes([0x58, len(value)]) + value


class Authenticator:
    """A passkey of software: an ES256 key and its sign count."""

    def __init__(self, *, flags: int = UP | UV, counts: bool = True) -> None:
        """Make the key and the credential ID.

        An authenticator that does not count signs with 0.
        """
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.credential_id = secrets.token_bytes(32)
        self.flags = flags
        self.counts = counts
        self.sign_count = 0

    def cose_key(self) -> bytes:
        """Return the public key as a COSE EC2 key with ES256."""
        numbers = self.key.public_key().public_numbers()
        x, y = numbers.x.to_bytes(32, "big"), numbers.y.to_bytes(32, "big")
        # {1: 2, 3: -7, -1: 1, -2: x, -3: y}
        return b"\xa5\x01\x02\x03\x26\x20\x01\x21" + cbor_bytes(x) + b"\x22" + cbor_bytes(y)

    def sign(
        self,
        challenge: str,
        user_handle: bytes | None,
        *,
        origin: str = ORIGIN,
        rp_id: str = settings.domain,
        extensions: bytes = b"",
        client: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Answer navigator.credentials.get() for challenge."""
        self.sign_count += self.counts
        flags = self.flags | (ED if extensions else 0)
        auth_data = (
            hashlib.sha256(rp_id.encode()).digest()
            + bytes([flags])
            + struct.pack(">I", self.sign_count)
            + extensions
        )
        client_data = {"type": "webauthn.get", "challenge": challenge, "origin": origin}
        client_data_json = json.dumps({**client_data, **(client or {})}).encode()
        signature = self.key.sign(
            auth_data + hashlib.sha256(client_data_json).digest(), ec.ECDSA(hashes.SHA256())
        )
        return {
            "id": bytes_to_base64url(self.credential_id),
            "rawId": bytes_to_base64url(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(client_data_json),
                "authenticatorData": bytes_to_base64url(auth_data),
                "signature": bytes_to_base64url(signature),
                "userHandle": bytes_to_base64url(user_handle) if user_handle else None,
            },
            "clientExtensionResults": {},
            "authenticatorAttachment": "platform",
        }


@pytest.fixture
async def account(session: AsyncSession) -> Account:
    """Create an account with an email."""
    row = Account(email="ana@example.com")
    session.add(row)
    await session.flush()
    return row


async def register(
    session: AsyncSession, account: Account, authenticator: Authenticator
) -> Passkey:
    """Store the passkey, as its registration would."""
    row = Passkey(
        account_id=account.id,
        credential_id=authenticator.credential_id,
        public_key=authenticator.cose_key(),
        sign_count=authenticator.sign_count,
        uv_initialized=bool(authenticator.flags & UV),
        transports=["internal"],
        backup_eligible=bool(authenticator.flags & BE),
        backup_state=bool(authenticator.flags & BS),
        name="Phone",
    )
    session.add(row)
    await session.flush()
    return row


@pytest.fixture
async def passkey(session: AsyncSession, account: Account) -> Authenticator:
    """Register an authenticator in the account."""
    authenticator = Authenticator()
    await register(session, account, authenticator)
    return authenticator


async def challenge(client: AsyncClient) -> str:
    """Ask for the options of a login and return its challenge."""
    response = await client.post("/api/auth/passkey/options")
    assert response.status_code == 200
    value: str = response.json()["challenge"]
    return value


async def sign_in(
    client: AsyncClient, credential: dict[str, Any], form: str = "token"
) -> Response:
    """Present an assertion to the login of the app or of the web."""
    return await client.post(f"/api/auth/passkey/{form}", json=credential)


async def actions(session: AsyncSession) -> list[str]:
    """Return the actions of the events, in order."""
    return list(await session.scalars(sa.select(EventLog.action).order_by(EventLog.id)))


async def failures(session: AsyncSession) -> int:
    """Return the consecutive failures of the passkey."""
    return (await session.scalars(sa.select(Passkey.failures))).one()


async def test_options_ask_a_challenge_of_16_bytes_for_10_minutes(client: AsyncClient) -> None:
    """The options: the domain, UV preferred, no passkey nor extension.

    The challenge is 16 bytes that live in Valkey 10 minutes.
    """
    response = await client.post("/api/auth/passkey/options")
    body = response.json()
    assert set(body) == {"challenge", "rpId", "allowCredentials", "userVerification"}
    assert (body["rpId"], body["allowCredentials"]) == (settings.domain, [])
    assert body["userVerification"] == "preferred"
    raw = base64url_to_bytes(body["challenge"])
    assert len(raw) == 16
    ttl = await store.client.ttl(passkeys.challenge_key(raw))
    assert 590 <= ttl <= 600


async def test_passkey_signs_in_the_web_and_the_app(
    client: AsyncClient, session: AsyncSession, account: Account, passkey: Authenticator
) -> None:
    """A valid assertion opens the web cookie or the app tokens."""
    credential = passkey.sign(await challenge(client), account.user_handle)
    response = await sign_in(client, credential, "cookie")
    assert response.status_code == 204
    assert sessions.COOKIE in SimpleCookie(response.headers["set-cookie"])
    credential = passkey.sign(await challenge(client), account.user_handle)
    response = await sign_in(client, credential)
    assert response.status_code == 200
    assert set(response.json()) == {"access_token", "token_type", "expires_in", "refresh_token"}
    assert "authn_login_success" in await actions(session)


async def test_challenge_is_used_once(
    client: AsyncClient, session: AsyncSession, account: Account, passkey: Authenticator
) -> None:
    """A challenge goes on its first use; one never issued fails."""
    credential = passkey.sign(await challenge(client), account.user_handle)
    assert (await sign_in(client, credential)).status_code == 200
    passkey.sign_count += 1
    assert (await sign_in(client, credential)).status_code == 401
    forged = passkey.sign(bytes_to_base64url(secrets.token_bytes(16)), account.user_handle)
    assert (await sign_in(client, forged)).status_code == 401
    assert await failures(session) == 0


@pytest.mark.parametrize(
    ("origin", "status"),
    [
        (f"https://{settings.domain}", 200),
        (f"https://app.{settings.domain}", 200),
        (f"https://panel.{settings.domain}", 200),
        ("android:apk-key-hash:test", 200),
        ("https://evil.example", 401),
        (f"http://app.{settings.domain}", 401),
        ("android:apk-key-hash:other", 401),
    ],
)
async def test_origin_is_a_web_surface_or_an_app(
    client: AsyncClient, account: Account, passkey: Authenticator, origin: str, status: int
) -> None:
    """The origin is a surface of domain or one of app_origins."""
    credential = passkey.sign(await challenge(client), account.user_handle, origin=origin)
    assert (await sign_in(client, credential)).status_code == status


async def test_rp_id_is_the_domain(
    client: AsyncClient, account: Account, passkey: Authenticator
) -> None:
    """An assertion for another RP ID is refused."""
    credential = passkey.sign(
        await challenge(client), account.user_handle, rp_id=f"app.{settings.domain}"
    )
    assert (await sign_in(client, credential)).status_code == 401


@pytest.mark.parametrize(
    "client_data", [{"crossOrigin": True}, {"topOrigin": "https://evil.example"}]
)
async def test_cross_origin_and_top_origin_are_refused(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    client_data: dict[str, object],
) -> None:
    """A ceremony inside another origin fails, and counts a failure."""
    credential = passkey.sign(await challenge(client), account.user_handle, client=client_data)
    assert (await sign_in(client, credential)).status_code == 401
    assert await failures(session) == 1


async def test_client_extension_results_must_be_empty(
    client: AsyncClient, account: Account, passkey: Authenticator
) -> None:
    """A clientExtensionResults that is not empty fails the login."""
    credential = passkey.sign(await challenge(client), account.user_handle)
    credential["clientExtensionResults"] = {"credProps": {"rk": True}}
    assert (await sign_in(client, credential)).status_code == 401


async def test_authenticator_extension_fails_and_is_named(
    client: AsyncClient, session: AsyncSession, account: Account, passkey: Authenticator
) -> None:
    """An extension in authData fails, and the event names it."""
    # {"credProtect": 1}
    extensions = b"\xa1\x6bcredProtect\x01"
    credential = passkey.sign(await challenge(client), account.user_handle, extensions=extensions)
    assert (await sign_in(client, credential)).status_code == 401
    details = await session.scalar(sa.select(EventLog.details))
    assert details == {"reason": "extensions", "extensions": ["credProtect"]}


async def test_backup_eligibility_must_be_the_stored_one(
    client: AsyncClient, session: AsyncSession, account: Account, passkey: Authenticator
) -> None:
    """A BE flag other than the registered one fails the login."""
    passkey.flags |= BE
    credential = passkey.sign(await challenge(client), account.user_handle)
    assert (await sign_in(client, credential)).status_code == 401
    assert await failures(session) == 1


async def test_user_handle_must_be_the_account(
    client: AsyncClient, account: Account, passkey: Authenticator
) -> None:
    """Another user handle, or none, fails the login."""
    for handle in (secrets.token_bytes(64), None):
        credential = passkey.sign(await challenge(client), handle)
        assert (await sign_in(client, credential)).status_code == 401


async def test_bad_signature_is_a_failure_that_stays(
    client: AsyncClient, session: AsyncSession, account: Account, passkey: Authenticator
) -> None:
    """Another key is a 401 that counts against the passkey."""
    other = Authenticator()
    other.credential_id = passkey.credential_id
    credential = other.sign(await challenge(client), account.user_handle)
    response = await sign_in(client, credential)
    assert response.status_code == 401
    assert response.headers["content-type"] == errors.PROBLEM_JSON
    assert await failures(session) == 1
    assert await actions(session) == ["authn_login_fail"]


async def test_unknown_passkey_is_a_401(client: AsyncClient, account: Account) -> None:
    """A credential ID that no account has is a 401."""
    credential = Authenticator().sign(await challenge(client), account.user_handle)
    assert (await sign_in(client, credential)).status_code == 401


@pytest.mark.parametrize(("stored", "presented"), [(5, 5), (5, 3), (5, 0), (0, 0)])
async def test_sign_count_that_does_not_grow_fails(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    stored: int,
    presented: int,
) -> None:
    """A sign count that is not zero, or stored, must grow.

    Both at zero, the authenticator does not count, and it passes.
    """
    authenticator = Authenticator(counts=presented != 0)
    row = await register(session, account, authenticator)
    row.sign_count = stored
    await session.flush()
    authenticator.sign_count = max(presented - 1, 0)
    credential = authenticator.sign(await challenge(client), account.user_handle)
    response = await sign_in(client, credential)
    expected = 200 if (stored, presented) == (0, 0) else 401
    assert response.status_code == expected


async def test_login_stores_sign_count_and_backup_state_after_the_checks(
    client: AsyncClient, session: AsyncSession, account: Account
) -> None:
    """A login keeps the new sign count, backup state and last use.

    uvInitialized stays as registered, and a failure changes none.
    """
    authenticator = Authenticator(flags=UP | BE)
    row = await register(session, account, authenticator)
    authenticator.flags |= BS | UV
    bad = authenticator.sign(await challenge(client), secrets.token_bytes(64))
    assert (await sign_in(client, bad)).status_code == 401
    await session.refresh(row)
    assert (row.sign_count, row.backup_state, row.last_used_at) == (0, False, None)
    good = authenticator.sign(await challenge(client), account.user_handle)
    assert (await sign_in(client, good)).status_code == 200
    await session.refresh(row)
    assert (row.sign_count, row.backup_state, row.uv_initialized) == (2, True, False)
    assert row.last_used_at is not None
    assert datetime.now(UTC) - row.last_used_at < timedelta(minutes=1)


async def test_passkey_waits_and_disables_like_any_authenticator(
    client: AsyncClient,
    session: AsyncSession,
    account: Account,
    passkey: Authenticator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Before its wait a passkey is a 429; disabled, a 403 of its type.

    A login after the wait resets its failures.
    """
    recorded: list[str] = []

    async def record(row: EventLog) -> None:
        """Keep the action of an event of its own transaction."""
        recorded.append(row.action)

    monkeypatch.setattr(events, "record", record)
    future = datetime.now(UTC) + timedelta(seconds=30)
    await session.execute(sa.update(Passkey).values(failures=5, retry_at=future))
    credential = passkey.sign(await challenge(client), account.user_handle)
    response = await sign_in(client, credential)
    assert response.status_code == 429
    assert "retry-after" in response.headers
    assert recorded == ["authn_login_fail_max"]
    await session.execute(sa.update(Passkey).values(retry_at=datetime.now(UTC)))
    assert (
        await sign_in(client, passkey.sign(await challenge(client), account.user_handle))
    ).is_success
    assert await failures(session) == 0
    await session.execute(sa.update(Passkey).values(disabled_at=datetime.now(UTC)))
    response = await sign_in(client, passkey.sign(await challenge(client), account.user_handle))
    assert response.status_code == 403
    assert response.json()["type"] == errors.AUTHENTICATOR_DISABLED.uri
