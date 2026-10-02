"""Every error response leaves as application/problem+json."""

import logging
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app import problems
from app.schemas.base import FieldError, Problem
from app.tracing import trace_id

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"
LOCATIONS = ("query", "path", "header", "cookie")


class AppError(Exception):
    """An error of the application, with its problem type."""

    def __init__(self, type_: str, title: str, status: int, detail: str | None = None) -> None:
        """Keep the RFC 9457 members of the problem."""
        super().__init__(detail or title)
        self.type = type_
        self.title = title
        self.status = status
        self.detail = detail


def respond(problem: Problem, headers: Mapping[str, str] | None = None) -> JSONResponse:
    """Serialize a problem with its media type."""
    return JSONResponse(
        problem.model_dump(mode="json", exclude_none=True),
        status_code=problem.status,
        headers=headers,
        media_type=PROBLEM_JSON,
    )


def blank(status: int, detail: str | None = None) -> Problem:
    """Build an about:blank problem, whose status says it all."""
    title = HTTPStatus(status).phrase
    return Problem(
        type="about:blank", title=title, status=status, detail=detail, traceId=trace_id.get()
    )


def pointer(path: tuple[int | str, ...]) -> str:
    """Build the RFC 6901 JSON Pointer of a body field."""
    tokens = (str(token).replace("~", "~0").replace("/", "~1") for token in path)
    return "".join(f"/{token}" for token in tokens)


def field_error(error: Mapping[str, Any]) -> FieldError:
    """Turn one Pydantic error into a pointer or a parameter."""
    location = tuple(error["loc"])
    detail = str(error["msg"])
    if location and location[0] in LOCATIONS:
        return FieldError(detail=detail, parameter=".".join(map(str, location[1:])))
    return FieldError(detail=detail, pointer=pointer(location[1:]))


async def app_error(_: Request, exc: Exception) -> JSONResponse:
    """Answer an AppError."""
    assert isinstance(exc, AppError)
    return respond(
        Problem(
            type=exc.type,
            title=exc.title,
            status=exc.status,
            detail=exc.detail,
            traceId=trace_id.get(),
        )
    )


async def http_error(_: Request, exc: Exception) -> JSONResponse:
    """Answer a Starlette HTTPException, keeping its headers."""
    assert isinstance(exc, HTTPException)
    detail = exc.detail if exc.detail != HTTPStatus(exc.status_code).phrase else None
    return respond(blank(exc.status_code, detail), exc.headers)


async def validation_error(_: Request, exc: Exception) -> JSONResponse:
    """Answer a validation error with one entry per field."""
    assert isinstance(exc, RequestValidationError)
    return respond(
        Problem(
            type=problems.VALIDATION,
            title="Invalid request",
            status=HTTPStatus.UNPROCESSABLE_CONTENT,
            errors=[field_error(error) for error in exc.errors()],
            traceId=trace_id.get(),
        )
    )


async def server_error(_: Request, exc: Exception) -> JSONResponse:
    """Answer an unexpected exception."""
    logger.exception("Unhandled error", exc_info=exc)
    return respond(blank(HTTPStatus.INTERNAL_SERVER_ERROR))


def install(app: FastAPI) -> None:
    """Register the handlers."""
    app.add_exception_handler(AppError, app_error)
    app.add_exception_handler(HTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(Exception, server_error)
