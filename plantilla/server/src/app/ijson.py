"""Reject a JSON body that is not an I-JSON message (RFC 7493).

plataformas/transversal.md, «OpenAPI y clientes»: UTF-8, no unpaired
surrogate or noncharacter, no number beyond a double, no member name
twice, and an object or an array at the top.
"""

import email.message
import json
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app import errors

LARGEST = 2**53 - 1


class NotIJson(ValueError):
    """A body that is JSON but not I-JSON."""


def members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build an object, failing on a repeated member name."""
    found: dict[str, Any] = {}
    for name, value in pairs:
        if name in found:
            raise NotIJson(f"Duplicate member name: {name}")
        found[name] = value
    return found


def integer(text: str) -> int:
    """Read an integer that a double holds exactly."""
    value = int(text)
    if abs(value) > LARGEST:
        raise NotIJson("Integer beyond 2**53 - 1")
    return value


def number(text: str) -> float:
    """Read a number no larger or finer than a double."""
    value = float(text)
    if Decimal(text) != Decimal(repr(value)):
        raise NotIJson("Number beyond the magnitude or precision of a double")
    return value


def constant(text: str) -> float:
    """Refuse NaN and Infinity, which are not JSON."""
    raise NotIJson(f"Not a JSON value: {text}")


def plain(text: str) -> bool:
    """Tell whether a string has no lone surrogate or noncharacter."""
    return not any(
        0xD800 <= ord(char) <= 0xDFFF
        or 0xFDD0 <= ord(char) <= 0xFDEF
        or ord(char) & 0xFFFE == 0xFFFE
        for char in text
    )


def strings(value: Any) -> bool:
    """Tell whether every name and string of a value is plain."""
    if isinstance(value, str):
        return plain(value)
    if isinstance(value, dict):
        return all(plain(name) and strings(item) for name, item in value.items())
    if isinstance(value, list):
        return all(strings(item) for item in value)
    return True


def problem(body: bytes) -> str | None:
    """Say why a JSON body is not I-JSON, or None if it is.

    A body that is not JSON at all is left to FastAPI, which answers it.
    """
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return "Not UTF-8"
    try:
        value = json.loads(
            text,
            object_pairs_hook=members,
            parse_int=integer,
            parse_float=number,
            parse_constant=constant,
        )
    except NotIJson as error:
        return str(error)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, (dict, list)):
        return "The top level is neither an object nor an array"
    if not strings(value):
        return "Unpaired surrogate or noncharacter"
    return None


def is_json(scope: Scope) -> bool:
    """Tell whether a body is JSON, as FastAPI decides it."""
    header = dict(scope["headers"]).get(b"content-type")
    if header is None:
        return False
    message = email.message.Message()
    message["content-type"] = header.decode("latin-1")
    subtype = message.get_content_subtype()
    return message.get_content_maintype() == "application" and (
        subtype == "json" or subtype.endswith("+json")
    )


class Checked:
    """Answer 422 to a JSON body that is not I-JSON."""

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Read the body, check it, and pass it on unchanged."""
        if scope["type"] != "http" or not is_json(scope):
            await self.app(scope, receive, send)
            return
        chunks: list[bytes] = []
        more = True
        while more:
            message = await receive()
            if message["type"] != "http.request":
                return
            chunks.append(message.get("body", b""))
            more = message.get("more_body", False)
        body = b"".join(chunks)
        reason = problem(body) if body else None
        if reason is not None:
            error = RequestValidationError(
                [{"type": "json_invalid", "loc": ("body",), "msg": reason, "input": {}}]
            )
            response = await errors.validation_error(Request(scope), error)
            await response(scope, receive, send)
            return
        sent = False

        async def replay() -> Message:
            """Hand the body over once, then whatever comes next."""
            nonlocal sent
            if sent:
                return await receive()
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay, send)


def install(app: FastAPI) -> None:
    """Check every JSON body of the app."""
    app.add_middleware(Checked)
