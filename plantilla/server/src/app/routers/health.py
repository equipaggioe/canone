"""The health check."""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from app.schemas.health import Health
from app.services import health

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def check() -> Health:
    """Answer 503 when the database does not."""
    if not await health.database_answers():
        raise HTTPException(HTTPStatus.SERVICE_UNAVAILABLE)
    return Health(status="ok")
