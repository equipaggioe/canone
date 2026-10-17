"""The health check."""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from app.services import health

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", status_code=HTTPStatus.NO_CONTENT)
async def check() -> None:
    """Answer 503 when the database does not."""
    if not await health.database_answers():
        raise HTTPException(HTTPStatus.SERVICE_UNAVAILABLE)
