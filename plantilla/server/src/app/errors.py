"""The app error, its problem types and their problem+json handlers."""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.schemas.base import Schema
from app.tracing import trace_id

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"
LOCATIONS = ("query", "path", "header", "cookie")

PROBLEMS = "https://DOMINIO/api/problems/"


@dataclass(frozen=True)
class ProblemType:
    """An RFC 9457 problem type and the page its URI serves."""

    name: str
    title: str
    status: HTTPStatus
    resolution: str

    @property
    def uri(self) -> str:
        """Identify the type."""
        return f"{PROBLEMS}{self.name}"


VALIDATION = ProblemType(
    "validation",
    "Invalid request",
    HTTPStatus.UNPROCESSABLE_CONTENT,
    "Fix each field or parameter listed in errors and send the request again.",
)
CLIENT_OUTDATED = ProblemType(
    "client-outdated",
    "Client outdated",
    HTTPStatus.BAD_REQUEST,
    "Install the latest version of the app.",
)
TYPES = {problem.name: problem for problem in (VALIDATION, CLIENT_OUTDATED)}


class FieldError(Schema):
    """One invalid field or parameter."""

    detail: str
    pointer: str | None = None
    parameter: str | None = None


class Problem(Schema):
    """An RFC 9457 problem details object."""

    type: str
    title: str
    status: int
    detail: str | None = None
    errors: list[FieldError] | None = None
    trace_id: str


class AppError(Exception):
    """An error of the application, with its problem type."""

    def __init__(self, problem: ProblemType, detail: str | None = None) -> None:
        """Keep the problem type and the detail of this occurrence."""
        super().__init__(detail or problem.title)
        self.problem = problem
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
        type="about:blank", title=title, status=status, detail=detail, traceId=trace_id()
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
            type=exc.problem.uri,
            title=exc.problem.title,
            status=exc.problem.status,
            detail=exc.detail,
            traceId=trace_id(),
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
            type=VALIDATION.uri,
            title=VALIDATION.title,
            status=VALIDATION.status,
            errors=[field_error(error) for error in exc.errors()],
            traceId=trace_id(),
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
