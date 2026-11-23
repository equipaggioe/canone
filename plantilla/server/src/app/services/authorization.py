"""The authorization code with PKCE, for the desktop and the web."""

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import store
from app.enums import TokenErrorCode
from app.errors import KeptError, TokenRefusal
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.schemas.auth import PasskeyCredential
from app.services import clients, passkeys
from app.services.sessions import Client

LIFETIME = timedelta(minutes=10)
S256 = "S256"


class Invalid(Exception):
    """A request without a registered client or return: no redirect."""


class Refused(Exception):
    """An error of the authorization endpoint, sent to the client."""

    def __init__(self, code: str) -> None:
        """Keep the error code of RFC 6749."""
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class Request:
    """A request that waits for the passkey of its user."""

    client_id: str
    redirect_uri: str
    # RFC 6749: the exchange repeats redirect_uri only if it came.
    redirect_given: bool
    code_challenge: str
    state: str | None


def digest(value: str) -> str:
    """Name a secret in Valkey by its SHA-256."""
    return hashlib.sha256(value.encode()).hexdigest()


def challenge_of(verifier: str) -> str:
    """Compute the S256 code_challenge of a code_verifier."""
    hashed = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()


def back(request: Request, **params: str) -> str:
    """Write the return to the client, with the state it sent."""
    if request.state is not None:
        params["state"] = request.state
    return f"{request.redirect_uri}?{urlencode(params)}"


def read(params: dict[str, str]) -> Request:
    """Check a request of the authorization endpoint.

    Without a registered client and return it is Invalid; any other
    error goes back to the client.
    """
    client = clients.registration(params.get("client_id", ""))
    if client is None:
        raise Invalid
    redirect = clients.redirect_uri(client, params.get("redirect_uri"))
    if redirect is None:
        raise Invalid
    request = Request(
        client_id=client.client_id,
        redirect_uri=redirect,
        redirect_given="redirect_uri" in params,
        code_challenge=params.get("code_challenge", ""),
        state=params.get("state"),
    )
    return request


def check(request: Request, params: dict[str, str]) -> None:
    """Refuse another response type, a scope, and no S256 challenge."""
    if "response_type" not in params:
        raise Refused("invalid_request")
    if params["response_type"] != "code":
        raise Refused("unsupported_response_type")
    if "scope" in params:
        raise Refused("invalid_scope")
    if not request.code_challenge or params.get("code_challenge_method") != S256:
        raise Refused("invalid_request")


async def wait(request: Request) -> str:
    """Keep a request until its passkey arrives, and return its ID."""
    key = secrets.token_urlsafe(32)
    await store.client.set(f"auth:request:{digest(key)}", json.dumps(asdict(request)), ex=LIFETIME)
    return key


async def grant(
    session: AsyncSession, key: str, credential: PasskeyCredential, client: Client
) -> str:
    """Sign in a waiting request with its passkey; return the redirect.

    The code is 256 random bits that live 10 minutes with the account.
    """
    stored = await store.client.get(f"auth:request:{digest(key)}")
    if stored is None:
        raise Invalid
    request = Request(**json.loads(stored))
    account = await passkeys.check(session, credential, client)
    await store.client.delete(f"auth:request:{digest(key)}")
    code = secrets.token_urlsafe(32)
    record = {**asdict(request), "account_id": str(account.id), "session_id": None}
    await store.client.set(f"auth:code:{digest(code)}", json.dumps(record), ex=LIFETIME)
    return back(request, code=code)


def required(params: dict[str, str], name: str) -> str:
    """Return a parameter of the exchange, or refuse its absence."""
    if name not in params:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    return params[name]


async def redeem(session: AsyncSession, params: dict[str, str]) -> Account:
    """Check an exchange of a code, once, and return its account.

    A code presented again deletes the session it created; the refusal
    keeps that. The caller opens the session and calls spent.
    """
    code = required(params, "code")
    client_id = required(params, "client_id")
    verifier = required(params, "code_verifier")
    refused = TokenRefusal(TokenErrorCode.INVALID_GRANT)
    stored = await store.client.get(f"auth:code:{digest(code)}")
    if stored is None:
        raise refused
    record: dict[str, Any] = json.loads(stored)
    if record["session_id"] is not None:
        await session.execute(
            sa.delete(AccountSession).where(AccountSession.id == UUID(record["session_id"]))
        )
        raise KeptError(refused)
    if record["redirect_given"] and "redirect_uri" not in params:
        raise TokenRefusal(TokenErrorCode.INVALID_REQUEST)
    redirect = params.get("redirect_uri", record["redirect_uri"])
    if client_id != record["client_id"] or redirect != record["redirect_uri"]:
        raise refused
    if not hmac.compare_digest(challenge_of(verifier), record["code_challenge"]):
        raise refused
    # Only one exchange claims the code, though two arrive together.
    claimed = await store.client.set(f"auth:claim:{digest(code)}", b"", nx=True, ex=LIFETIME)
    if not claimed:
        raise refused
    return await session.get_one(Account, UUID(record["account_id"]))


async def spent(code: str, session_id: UUID) -> None:
    """Mark a code as used, with the session it created."""
    key = f"auth:code:{digest(code)}"
    stored = await store.client.get(key)
    if stored is None:
        return
    record = {**json.loads(stored), "session_id": str(session_id)}
    await store.client.set(key, json.dumps(record), keepttl=True)


@dataclass(frozen=True)
class Flow:
    """The web flow that the server runs: its state and its verifier."""

    state: str
    verifier: str


async def start_web(host: str) -> tuple[str, str]:
    """Start the web flow of a surface; return its ID and request URL.

    The verifier is 32 random bytes in base64url.
    """
    flow = Flow(state=secrets.token_urlsafe(32), verifier=secrets.token_urlsafe(32))
    key = secrets.token_urlsafe(32)
    await store.client.set(f"auth:flow:{digest(key)}", json.dumps(asdict(flow)), ex=LIFETIME)
    query = urlencode(
        {
            "response_type": "code",
            "client_id": clients.WEB,
            "redirect_uri": clients.web_return(host),
            "code_challenge": challenge_of(flow.verifier),
            "code_challenge_method": S256,
            "state": flow.state,
        }
    )
    return key, f"/api/auth/authorize?{query}"


async def take_flow(key: str) -> Flow | None:
    """Take a web flow once, by the ID of its cookie."""
    stored = await store.client.getdel(f"auth:flow:{digest(key)}")
    return Flow(**json.loads(stored)) if stored is not None else None
