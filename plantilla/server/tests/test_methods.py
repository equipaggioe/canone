"""The ways to sign in that the product chooses."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection

from app import errors, methods
from app.enums import Method
from app.main import api_router
from tests.authenticator import Authenticator


@pytest.mark.usefixtures("database")
async def test_a_method_the_product_does_not_use_has_no_routes() -> None:
    """Without a method its routes are gone; the rest of /api stays.

    The authorization code goes with the passkey, which its page asks.
    """
    probe = FastAPI()
    errors.install(probe)
    probe.include_router(api_router(frozenset()))
    async with AsyncClient(transport=ASGITransport(app=probe), base_url="http://test") as client:
        for path in (
            "/api/auth/password/token",
            "/api/auth/password/cookie",
            "/api/auth/reauth/password",
            "/api/auth/passkey/options",
            "/api/auth/passkey/token",
            "/api/auth/reauth/passkey",
            "/api/auth/register/options",
            "/api/account/passkeys/options",
            "/api/auth/authorize",
            "/api/auth/sms/code",
            "/api/auth/sms/cookie",
            "/api/auth/sms/token",
            "/api/auth/reauth/sms/code",
            "/api/auth/reauth/sms",
            "/api/auth/recovery/code",
            "/api/auth/recovery/password",
            "/api/auth/recovery/options",
            "/api/auth/recovery/passkey",
            "/api/account/phone/enable",
            "/api/account/passkeys/00000000-0000-4000-8000-000000000000/enable",
        ):
            assert (await client.post(path, json={})).status_code == 404, path
        assert (await client.put("/api/account/password", json={})).status_code == 404
        assert (await client.get("/api/auth/web/start")).status_code == 404
        assert (await client.put("/api/account/recovery-code", json={})).status_code == 404
        assert (await client.get("/api/account/recovery")).status_code == 404
        assert (await client.get("/api/health")).status_code == 204


@pytest.mark.parametrize(
    ("chosen", "field"), [(Method.PASSKEY, "password"), (Method.PASSWORD, "credential")]
)
async def test_registration_takes_only_the_methods_of_the_product(
    client: AsyncClient,
    database: AsyncConnection,
    monkeypatch: pytest.MonkeyPatch,
    chosen: Method,
    field: str,
) -> None:
    """An authenticator the product does not offer is a 422 on it."""
    monkeypatch.setattr(methods, "METHODS", frozenset({chosen}))
    body: dict[str, object] = {"email": "bea@example.com", "code": "123456"}
    if field == "password":
        body["password"] = "Staple of a purple ocean"
    else:
        body["passkeyName"] = "Phone"
        body["credential"] = Authenticator().create("AAAA")
    response = await client.post("/api/auth/register/token", json=body)
    assert response.status_code == 422
    other = Method.PASSWORD if chosen == Method.PASSKEY else Method.PASSKEY
    assert response.json()["errors"] == [
        {"detail": f"The product takes no {other}", "pointer": f"/{field}"}
    ]
