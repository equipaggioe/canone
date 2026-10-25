"""The health check, and what to alert on."""

import hmac
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.schemas.health import HealthEvents
from app.services import health

router = APIRouter(prefix="/health", tags=["health"])
bearer = HTTPBearer(auto_error=False)


@router.get("", status_code=HTTPStatus.NO_CONTENT)
async def check() -> None:
    """Answer 503 when the database does not."""
    if not await health.database_answers():
        raise HTTPException(HTTPStatus.SERVICE_UNAVAILABLE)


def check_health_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> None:
    """Answer 401 without the token, compared in constant time."""
    token = credentials.credentials if credentials else ""
    if not hmac.compare_digest(token.encode(), settings.health_token.encode()):
        raise HTTPException(HTTPStatus.UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"})


@router.get("/events", dependencies=[Depends(check_health_token)])
async def events() -> HealthEvents:
    """Tell the last critical event, the last backup and the disk."""
    free, total = health.disk_usage()
    return HealthEvents(
        last_critical_at=await health.last_critical(),
        last_backup_at=health.last_backup(),
        disk_free_bytes=free,
        disk_total_bytes=total,
    )
