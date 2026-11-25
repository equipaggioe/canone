"""The subscription of a browser, which receives the pushes."""

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import PrincipalDep, SessionDep, signed_in
from app.enums import SessionKind
from app.schemas.web_push import PushKey, SubscriptionRegistration
from app.services import web_push
from app.translations import language

router = APIRouter(prefix="/account/push", tags=["push"])


@router.get("/key", dependencies=[Depends(signed_in)])
async def get_key() -> PushKey:
    """Return the key that the web subscribes with."""
    return PushKey(key=web_push.PUBLIC_KEY)


@router.put("/subscription", status_code=HTTPStatus.NO_CONTENT)
async def put_subscription(
    request: Request, session: SessionDep, principal: PrincipalDep, body: SubscriptionRegistration
) -> None:
    """Send the pushes of the session to this browser."""
    if principal.session.kind != SessionKind.WEB:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Only the web has a subscription")
    asked = language(request.headers.get("accept-language", ""))
    await web_push.register(session, principal.session.id, body, asked)
