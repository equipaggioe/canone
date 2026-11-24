"""The authorization code with PKCE, for the desktop and the web."""

import re
import secrets
from collections.abc import AsyncIterator
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
import sqlalchemy as sa
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from webauthn.helpers import base64url_to_bytes

from app import store
from app.config import settings
from app.enums import Method, Role
from app.main import app
from app.methods import METHODS
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.services import authorization, clients, sessions
from tests.authenticator import Authenticator, register

pytestmark = pytest.mark.skipif(
    Method.PASSKEY not in METHODS, reason="the product offers no passkey"
)

HOST = f"app.{settings.domain}"
DESKTOP = clients.Registration("desktop", frozenset({"http://127.0.0.1/callback"}))
RETURN = "http://127.0.0.1:5555/callback"
VERIFIER = secrets.token_urlsafe(32)


@pytest.fixture
async def browser(database: AsyncConnection) -> AsyncIterator[AsyncClient]:
    """Call the app as a browser on the web surface."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=f"https://{HOST}") as client:
        yield client


@pytest.fixture(autouse=True)
def desktop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Register an app of the desktop that returns on loopback."""
    monkeypatch.setitem(clients.CLIENTS, DESKTOP.client_id, DESKTOP)


@pytest.fixture
async def passkey(session: AsyncSession) -> tuple[Account, Authenticator]:
    """Create an account with a passkey."""
    account = Account(email="ana@example.com", role=Role.USER, language="es")
    session.add(account)
    await session.flush()
    authenticator = Authenticator()
    await register(session, account, authenticator)
    return account, authenticator


def params(**changes: str | None) -> dict[str, str]:
    """Build a valid request of the desktop app, with changes."""
    base: dict[str, str | None] = {
        "response_type": "code",
        "client_id": DESKTOP.client_id,
        "redirect_uri": RETURN,
        "code_challenge": authorization.challenge_of(VERIFIER),
        "code_challenge_method": "S256",
        "state": "xyz",
    }
    return {key: value for key, value in {**base, **changes}.items() if value is not None}


def returned(response: Response) -> dict[str, str]:
    """Read the parameters of the redirect to the client."""
    assert response.status_code == 303
    query = parse_qs(urlsplit(response.headers["location"]).query)
    return {key: values[0] for key, values in query.items()}


async def sign_in(
    browser: AsyncClient, passkey: tuple[Account, Authenticator], request: dict[str, str]
) -> str:
    """Open the page, sign in with the passkey, return the redirect."""
    page = await browser.get("/api/auth/authorize", params=request)
    assert page.status_code == 200
    match = re.search(r'data-request="([^"]+)"', page.text)
    assert match is not None
    account, authenticator = passkey
    options = (await browser.post("/api/auth/passkey/options")).json()
    credential = authenticator.sign(options["challenge"], account.user_handle)
    body = {"request": match.group(1), "credential": credential}
    response = await browser.post("/api/auth/authorize", json=body)
    assert response.status_code == 200
    redirect: str = response.json()["redirect"]
    return redirect


async def exchange(client: AsyncClient, **fields: str) -> Response:
    """Present a code to the token endpoint."""
    return await client.post(
        "/api/auth/token", data={"grant_type": "authorization_code", **fields}
    )


async def code_of(browser: AsyncClient, passkey: tuple[Account, Authenticator]) -> str:
    """Sign in the desktop app and return its code."""
    redirect = await sign_in(browser, passkey, params())
    return parse_qs(urlsplit(redirect).query)["code"][0]


@pytest.mark.parametrize(
    "request_params",
    [
        params(client_id=None),
        params(client_id="other"),
        params(redirect_uri="http://localhost:5555/callback"),
        params(redirect_uri="http://[::1]:5555/callback"),
        params(redirect_uri="http://127.0.0.1:5555/other"),
        params(redirect_uri=None),
    ],
)
async def test_unregistered_client_or_return_shows_the_error(
    browser: AsyncClient, request_params: dict[str, str]
) -> None:
    """Without a registered client and return, the error is a page."""
    response = await browser.get("/api/auth/authorize", params=request_params)
    assert response.status_code == 400
    assert "location" not in response.headers
    assert response.headers["content-type"].startswith("text/html")


async def test_repeated_client_or_return_shows_the_error(browser: AsyncClient) -> None:
    """A repeated client_id or redirect_uri cannot be trusted."""
    query = urlencode(params()) + "&client_id=desktop"
    response = await browser.get(f"/api/auth/authorize?{query}")
    assert response.status_code == 400


@pytest.mark.parametrize("port", ["5555", "61000"])
async def test_loopback_return_takes_any_port(browser: AsyncClient, port: str) -> None:
    """The port of a loopback return may be any."""
    redirect = f"http://127.0.0.1:{port}/callback"
    response = await browser.get("/api/auth/authorize", params=params(redirect_uri=redirect))
    assert response.status_code == 200


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"response_type": "token"}, "unsupported_response_type"),
        ({"response_type": None}, "invalid_request"),
        ({"scope": "openid"}, "invalid_scope"),
        ({"code_challenge": None}, "invalid_request"),
        ({"code_challenge_method": "plain"}, "invalid_request"),
        ({"code_challenge_method": None}, "invalid_request"),
    ],
)
async def test_authorization_errors_go_back_with_the_state(
    browser: AsyncClient, changes: dict[str, str | None], error: str
) -> None:
    """Another response type, a scope or no S256 go back as errors."""
    response = await browser.get("/api/auth/authorize", params=params(**changes))
    assert returned(response) == {"error": error, "state": "xyz"}


async def test_authorization_parameters(browser: AsyncClient) -> None:
    """Repeated: invalid_request; empty: absent; unknown: ignored."""
    query = urlencode(params()) + "&state=again"
    assert returned(await browser.get(f"/api/auth/authorize?{query}"))["error"] == (
        "invalid_request"
    )
    query = urlencode(params()) + "&scope=&unknown=1"
    assert (await browser.get(f"/api/auth/authorize?{query}")).status_code == 200


async def test_page_loads_nothing_from_other_sites(browser: AsyncClient) -> None:
    """The page brings its style and script, and names no other site."""
    page = (await browser.get("/api/auth/authorize", params=params())).text
    assert not re.search(r"(src|href)=", page)
    assert not re.search(r"https?://", page)


@pytest.mark.parametrize("language", ["es-CL,en;q=0.5", "en", ""])
async def test_page_speaks_the_language_asked_or_the_base(
    browser: AsyncClient, language: str
) -> None:
    """The page takes its texts from the catalog; es if none matches."""
    headers = {"Accept-Language": language}
    page = await browser.get("/api/auth/authorize", params=params(), headers=headers)
    assert '<html lang="es">' in page.text
    assert "Entrar con passkey" in page.text


async def test_page_asks_the_passkey_with_a_web_session(
    browser: AsyncClient, passkey: tuple[Account, Authenticator]
) -> None:
    """An open session of the web does not skip the passkey."""
    account, authenticator = passkey
    options = (await browser.post("/api/auth/passkey/options")).json()
    credential = authenticator.sign(options["challenge"], account.user_handle)
    login = await browser.post("/api/auth/passkey/cookie", json=credential)
    token = SimpleCookie(login.headers["set-cookie"])[sessions.COOKIE].value
    cookie = {"Cookie": f"{sessions.COOKIE}={token}"}
    page = await browser.get("/api/auth/authorize", params=params(), headers=cookie)
    assert page.status_code == 200
    assert 'data-request="' in page.text


async def test_code_goes_back_with_the_state_and_gives_the_tokens(
    browser: AsyncClient, passkey: tuple[Account, Authenticator]
) -> None:
    """The passkey gives a code of 256 bits for 10 minutes, with state.

    The exchange answers the tokens, not to be cached.
    """
    redirect = await sign_in(browser, passkey, params())
    assert redirect.startswith(f"{RETURN}?")
    back = parse_qs(urlsplit(redirect).query)
    assert back["state"] == ["xyz"]
    code = back["code"][0]
    assert len(base64url_to_bytes(code)) == 32
    ttl = await store.client.ttl(f"auth:code:{authorization.digest(code)}")
    assert 590 <= ttl <= 600
    response = await exchange(
        browser, code=code, client_id="desktop", redirect_uri=RETURN, code_verifier=VERIFIER
    )
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    body = response.json()
    assert set(body) == {"access_token", "token_type", "expires_in", "refresh_token"}
    assert (body["token_type"], body["expires_in"]) == ("Bearer", 900)


@pytest.mark.parametrize(
    "changes",
    [
        {"client_id": "other"},
        {"redirect_uri": "http://127.0.0.1:5555/other"},
        {"code_verifier": secrets.token_urlsafe(32)},
        {"code": secrets.token_urlsafe(32)},
    ],
)
async def test_code_is_bound_to_client_return_and_verifier(
    browser: AsyncClient, passkey: tuple[Account, Authenticator], changes: dict[str, str]
) -> None:
    """Another client, return, verifier or code: invalid_grant."""
    code = await code_of(browser, passkey)
    fields = {
        "code": code,
        "client_id": "desktop",
        "redirect_uri": RETURN,
        "code_verifier": VERIFIER,
    }
    response = await exchange(browser, **{**fields, **changes})
    assert response.json() == {"error": "invalid_grant"}


@pytest.mark.parametrize("missing", ["code", "client_id", "code_verifier", "redirect_uri"])
async def test_exchange_without_a_parameter_is_invalid_request(
    browser: AsyncClient, passkey: tuple[Account, Authenticator], missing: str
) -> None:
    """A required parameter that is missing: invalid_request, not 422.

    redirect_uri is required because the request carried it.
    """
    code = await code_of(browser, passkey)
    fields = {
        "code": code,
        "client_id": "desktop",
        "redirect_uri": RETURN,
        "code_verifier": VERIFIER,
    }
    del fields[missing]
    response = await exchange(browser, **fields)
    assert response.status_code == 400
    assert response.json() == {"error": "invalid_request"}


async def test_code_presented_twice_deletes_its_session(
    browser: AsyncClient, session: AsyncSession, passkey: tuple[Account, Authenticator]
) -> None:
    """A code goes once; again, invalid_grant, and its session goes."""
    code = await code_of(browser, passkey)
    fields = {
        "code": code,
        "client_id": "desktop",
        "redirect_uri": RETURN,
        "code_verifier": VERIFIER,
    }
    first = await exchange(browser, **fields)
    assert first.status_code == 200
    assert (await exchange(browser, **fields)).json() == {"error": "invalid_grant"}
    assert (await session.scalars(sa.select(AccountSession.id))).all() == []


async def web_flow(browser: AsyncClient) -> tuple[str, dict[str, str]]:
    """Start the web flow; return its cookie and its request."""
    response = await browser.get("/api/auth/web/start")
    assert response.status_code == 303
    location = urlsplit(response.headers["location"])
    assert location.path == "/api/auth/authorize"
    request = {key: values[0] for key, values in parse_qs(location.query).items()}
    return response.headers["set-cookie"], request


async def test_web_flow_keeps_state_and_verifier_behind_a_cookie(browser: AsyncClient) -> None:
    """The flow cookie is __Host-, Secure, HttpOnly and Strict.

    The verifier is 32 random bytes; the request asks S256 for the web.
    """
    cookie, request = await web_flow(browser)
    morsel = SimpleCookie(cookie)["__Host-flow"]
    assert (morsel["secure"], morsel["httponly"], morsel["samesite"]) == (True, True, "strict")
    assert morsel["path"] == "/"
    assert request["client_id"] == "web"
    assert request["redirect_uri"] == f"https://{HOST}/api/auth/web/return"
    assert request["code_challenge_method"] == "S256"
    flow = await authorization.take_flow(morsel.value)
    assert flow is not None
    assert len(base64url_to_bytes(flow.verifier)) == 32
    assert authorization.challenge_of(flow.verifier) == request["code_challenge"]


async def test_web_flow_returns_with_the_cookie_of_the_session(
    browser: AsyncClient, session: AsyncSession, passkey: tuple[Account, Authenticator]
) -> None:
    """The return exchanges the code, sets the session, goes to the app.

    It takes the flow once and deletes its cookie.
    """
    cookie, request = await web_flow(browser)
    flow = SimpleCookie(cookie)["__Host-flow"].value
    redirect = urlsplit(await sign_in(browser, passkey, request))
    headers = {"Cookie": f"__Host-flow={flow}"}
    back = await browser.get(f"{redirect.path}?{redirect.query}", headers=headers)
    assert back.status_code == 303
    assert back.headers["location"] == "/"
    cookies = SimpleCookie()
    for value in back.headers.get_list("set-cookie"):
        cookies.load(value)
    assert cookies["__Host-flow"]["max-age"] == "0"
    assert cookies[sessions.COOKIE].value
    kinds = await session.scalars(sa.select(AccountSession.kind))
    assert [kind.value for kind in kinds] == ["web"]
    again = await browser.get(f"{redirect.path}?{redirect.query}", headers=headers)
    assert again.status_code == 400
    assert again.headers["content-type"].startswith("text/html")


async def test_web_return_with_another_state_fails(
    browser: AsyncClient, passkey: tuple[Account, Authenticator]
) -> None:
    """A return whose state is not the one of its flow is refused."""
    cookie, request = await web_flow(browser)
    flow = SimpleCookie(cookie)["__Host-flow"].value
    redirect = urlsplit(await sign_in(browser, passkey, request))
    query = {**parse_qs(redirect.query), "state": ["other"]}
    response = await browser.get(
        redirect.path,
        params={k: v[0] for k, v in query.items()},
        headers={"Cookie": f"__Host-flow={flow}"},
    )
    assert response.status_code == 400
