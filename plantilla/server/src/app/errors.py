"""The app error, its problem types and their problem+json handlers."""

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.json_schema import models_json_schema
from starlette.exceptions import HTTPException

from app.enums import EventLevel
from app.schemas.base import Schema
from app.services import events
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
    trace_id: str


class ValidationProblem(Problem):
    """A problem of type validation, with one entry per field."""

    errors: list[FieldError]


def described(description: str, schema: str) -> dict[str, Any]:
    """Describe an error response whose body is a problem schema."""
    return {
        "description": description,
        "content": {PROBLEM_JSON: {"schema": {"$ref": f"#/components/schemas/{schema}"}}},
    }


# Every operation declares its errors as problem+json.
RESPONSES: dict[int | str, dict[str, Any]] = {
    HTTPStatus.UNPROCESSABLE_CONTENT.value: described("Validation error", "ValidationProblem"),
    "4XX": described("Client error", "Problem"),
    "5XX": described("Server error", "Problem"),
}


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


def validation_event(found: list[Mapping[str, Any]]) -> tuple[str, EventLevel]:
    """Name the event of a validation error in the OWASP vocabulary.

    A field the server does not expect is probing; a value outside its
    list means a client that was tampered with.
    """
    kinds = {error["type"] for error in found}
    if "extra_forbidden" in kinds:
        return "malicious_extraneous", EventLevel.CRITICAL
    if kinds & {"enum", "literal_error"}:
        return "input_validation_discrete_fail", EventLevel.WARN
    return "input_validation_fail", EventLevel.WARN


async def validation_error(request: Request, exc: Exception) -> JSONResponse:
    """Answer a validation error, one entry per field, and log it.

    A body that is not JSON is a 400, with no entries.
    """
    assert isinstance(exc, RequestValidationError)
    found = list(exc.errors())
    fields = [field_error(error) for error in found]
    action, level = validation_event(found)
    await events.record(
        events.event(
            action,
            level,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"fields": sorted(field.pointer or field.parameter or "" for field in fields)},
        )
    )
    # RFC 9110: a 422 says the syntax is right, so not JSON is a 400.
    if {error["type"] for error in found} == {"json_invalid"}:
        return respond(blank(HTTPStatus.BAD_REQUEST, "The body is not JSON"))
    return respond(
        ValidationProblem(
            type=VALIDATION.uri,
            title=VALIDATION.title,
            status=VALIDATION.status,
            errors=fields,
            traceId=trace_id(),
        )
    )


async def server_error(_: Request, exc: Exception) -> JSONResponse:
    """Answer an unexpected exception."""
    logger.exception("Unhandled error", exc_info=exc)
    return respond(blank(HTTPStatus.INTERNAL_SERVER_ERROR))


def with_problems(build: Callable[[], dict[str, Any]]) -> Callable[[], dict[str, Any]]:
    """Add to the OpenAPI the problem schemas of RESPONSES."""

    def openapi() -> dict[str, Any]:
        """Build the OpenAPI once, with the problem schemas."""
        document = build()
        _, schemas = models_json_schema(
            [(Problem, "serialization"), (ValidationProblem, "serialization")],
            ref_template="#/components/schemas/{model}",
        )
        document.setdefault("components", {}).setdefault("schemas", {}).update(schemas["$defs"])
        return document

    return openapi


def install(app: FastAPI) -> None:
    """Register the handlers, and the schemas of the problems."""
    app.add_exception_handler(AppError, app_error)
    app.add_exception_handler(HTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(Exception, server_error)
    # FastAPI documents this way to extend the OpenAPI of an app.
    app.openapi = with_problems(app.openapi)  # pyrefly: ignore[method-assign]
