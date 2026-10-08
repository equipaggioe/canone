"""The documentation of each problem type, served at its URI."""

from html import escape
from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from app.errors import TYPES

router = APIRouter(prefix="/problems", tags=["problems"], include_in_schema=False)


@router.get("/{name}", response_class=HTMLResponse)
async def describe(name: str) -> str:
    """Explain a problem type and how to resolve it."""
    problem = TYPES.get(name)
    if problem is None:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    title = escape(problem.title)
    return (
        f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title></head>"
        f"<body><h1>{title}</h1><p>Status: {problem.status.value}</p>"
        f"<p>{escape(problem.resolution)}</p></body></html>"
    )
