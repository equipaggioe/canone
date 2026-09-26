"""W3C Trace Context: el trace-id de cada request, para el log y el error."""

import logging
import re
import secrets
from contextvars import ContextVar
from typing import override

from starlette.types import ASGIApp, Receive, Scope, Send

# version-trace_id-parent_id-flags. La versión ff y los ids en cero son
# inválidos; una versión mayor que 00 puede traer campos al final.
TRACEPARENT = re.compile(
    r"(?!ff)([0-9a-f]{2})-(?!0{32})([0-9a-f]{32})-(?!0{16})[0-9a-f]{16}-[0-9a-f]{2}(-.*)?"
)

trace_id: ContextVar[str] = ContextVar("trace_id")


def parse_trace_id(traceparent: str) -> str | None:
    match = TRACEPARENT.fullmatch(traceparent)
    if match is None or (match.group(1) == "00" and match.group(3) is not None):
        return None
    return match.group(2)


class TraceContextMiddleware:
    """Toma el trace-id del traceparent, o empieza una traza si falta o es inválido."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope["headers"])
            received = parse_trace_id(headers.get(b"traceparent", b"").decode("latin-1"))
            # Sin reset: el handler de 500 corre por fuera de este middleware y
            # necesita el valor. Cada request corre en su propia tarea, con su
            # propia copia del contexto, así que no pasa a otro request.
            trace_id.set(received or secrets.token_hex(16))
        await self.app(scope, receive, send)


class TraceIdFilter(logging.Filter):
    """Pone el trace-id en cada registro, para el %(trace_id)s del formato."""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id.get("-")
        return True
