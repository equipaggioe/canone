"""The W3C trace-id of each request, in the log and in the errors."""

import logging
import secrets
from contextvars import ContextVar

from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send

trace_id: ContextVar[str] = ContextVar("trace_id")


class TraceMiddleware:
    """Start a trace for every request and every WebSocket."""

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Set a new trace-id, ignoring any traceparent."""
        if scope["type"] in ("http", "websocket"):
            # ADR-0015: not reset, the handler of unexpected
            # exceptions runs outside every middleware.
            trace_id.set(secrets.token_hex(16))
        await self.app(scope, receive, send)


class TraceFilter(logging.Filter):
    """Put the trace-id on every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Leave it empty outside a request."""
        record.trace_id = trace_id.get("")
        return True


def install(app: FastAPI) -> None:
    """Add the middleware and print the trace-id in every log line."""
    app.add_middleware(TraceMiddleware)
    handler = logging.StreamHandler()
    handler.addFilter(TraceFilter())
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(trace_id)s %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])
