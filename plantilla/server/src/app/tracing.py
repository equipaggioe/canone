"""The W3C trace-id of each request, in the log and in the errors."""

import logging

from opentelemetry import propagate, trace
from opentelemetry.context import Context
from opentelemetry.propagators.textmap import CarrierT, Getter, Setter, TextMapPropagator
from opentelemetry.sdk.trace import TracerProvider


class IgnoreTraceparent(TextMapPropagator):
    """Start a trace for every request and every WebSocket."""

    def extract(
        self,
        carrier: CarrierT,
        context: Context | None = None,
        getter: Getter[CarrierT] | None = None,
    ) -> Context:
        """Drop any traceparent: the client picks no trace-id."""
        return Context()

    def inject(
        self,
        carrier: CarrierT,
        context: Context | None = None,
        setter: Setter[CarrierT] | None = None,
    ) -> None:
        """Send no trace context."""

    @property
    def fields(self) -> set[str]:
        """Read and write no header."""
        return set()


def trace_id() -> str:
    """Read the trace-id of the current span, empty outside one."""
    context = trace.get_current_span().get_span_context()
    return trace.format_trace_id(context.trace_id) if context.is_valid else ""


class TraceFilter(logging.Filter):
    """Put the trace-id on every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Leave it empty outside a trace."""
        record.trace_id = trace_id()
        return True


def install() -> None:
    """Set the tracer provider and log the trace-id."""
    propagate.set_global_textmap(IgnoreTraceparent())
    trace.set_tracer_provider(TracerProvider())
    handler = logging.StreamHandler()
    handler.addFilter(TraceFilter())
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(trace_id)s %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])
