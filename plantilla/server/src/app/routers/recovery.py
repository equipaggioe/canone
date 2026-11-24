"""Recovering an account: the code, the saved code, what waits.

main.py mounts these routes only if the product offers the passkey or
the password, which a recovery restores.
"""

from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.dependencies import ClientDep, PrincipalDep, ReauthenticatedDep, SessionDep, public
from app.routers.auth import accepted
from app.schemas.account import RecoveryView
from app.schemas.auth import Identifier, RecoveryCodeView
from app.services import recovery
from app.services.recovery import Outcome

router = APIRouter(tags=["recovery"])

# A recovery applies at once, waits 24 hours, or spends the saved code
# and answers the new one.
RECOVERED: dict[int | str, dict[str, Any]] = {
    HTTPStatus.NO_CONTENT.value: {"description": "Recovered at once"},
    HTTPStatus.ACCEPTED.value: {"description": "Recovers in 24 hours"},
}
CREATED: dict[int | str, dict[str, Any]] = {
    HTTPStatus.CREATED.value: {"model": RecoveryCodeView, "description": "The account had none"}
}


def answer(outcome: Outcome) -> Response:
    """Answer how a recovery ended."""
    if outcome.pending:
        return Response(status_code=HTTPStatus.ACCEPTED)
    if outcome.recovery_code is None:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    body = RecoveryCodeView(recovery_code=outcome.recovery_code)
    return JSONResponse(body.model_dump(mode="json"))


@router.post(
    "/auth/recovery/code", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(public)]
)
async def code(request: Request, session: SessionDep, body: Identifier, caller: ClientDep) -> None:
    """Send the code to recover to an email or a phone of an account."""
    host = request.headers.get("host", "")
    await recovery.send_code(session, body, caller, accepted(request), host)


@router.get("/account/recovery")
async def get_pending(session: SessionDep, principal: PrincipalDep) -> RecoveryView:
    """Show the recovery of the account that waits, or answer 404."""
    row = await recovery.pending(session, principal.account)
    if row is None:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    return RecoveryView.model_validate(row)


@router.delete("/account/recovery", status_code=HTTPStatus.NO_CONTENT)
async def cancel(session: SessionDep, principal: PrincipalDep, caller: ClientDep) -> None:
    """Cancel the recovery of the account that waits."""
    if not await recovery.cancel(session, principal.account, caller, "holder"):
        raise HTTPException(HTTPStatus.NOT_FOUND)


@router.put("/account/recovery-code", responses=CREATED)
async def put_code(
    response: Response, session: SessionDep, principal: ReauthenticatedDep, caller: ClientDep
) -> RecoveryCodeView:
    """Make a new saved code, shown once; the previous one stops."""
    saved, new = await recovery.create_saved(session, principal.account, caller)
    if new:
        response.status_code = HTTPStatus.CREATED
    return RecoveryCodeView(recovery_code=saved)
