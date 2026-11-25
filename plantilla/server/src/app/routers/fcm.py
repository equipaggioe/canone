"""The installation of an app, which receives the pushes by FCM."""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request

from app.dependencies import PrincipalDep, SessionDep
from app.enums import SessionKind
from app.schemas.fcm import FidRegistration
from app.services import fcm
from app.translations import language

router = APIRouter(prefix="/account/push", tags=["push"])


@router.put("/fid", status_code=HTTPStatus.NO_CONTENT)
async def put_fid(
    request: Request, session: SessionDep, principal: PrincipalDep, body: FidRegistration
) -> None:
    """Send the pushes of the session to this installation."""
    if principal.session.kind != SessionKind.APP:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Only an app has an installation")
    asked = language(request.headers.get("accept-language", ""))
    await fcm.register(session, principal.session.id, body, asked)
