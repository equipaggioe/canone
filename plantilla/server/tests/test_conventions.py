from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.enums import ProblemType
from app.main import app

PROBLEM_REF = "#/components/schemas/ProblemDetails"
TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"
TRACEPARENT = f"00-{TRACE_ID}-00f067aa0ba902b7-01"


@pytest.mark.parametrize("problem_type", [t for t in ProblemType if t != "about:blank"])
async def test_problem_type_is_documented(problem_type: ProblemType) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(problem_type.value)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def problem_schema(operation: dict[str, Any], status: str) -> str | None:
    content = operation["responses"].get(status, {}).get("content", {})
    ref: str | None = content.get("application/problem+json", {}).get("schema", {}).get("$ref")
    return ref


def test_every_operation_declares_problem_details() -> None:
    missing = [
        f"{method.upper()} {path} {status}"
        for path, operations in app.openapi()["paths"].items()
        for method, operation in operations.items()
        for status in ("4XX", "422", "5XX")
        if problem_schema(operation, status) != PROBLEM_REF
    ]
    assert not missing


async def test_error_carries_trace_id() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/problems/not-a-type", headers={"traceparent": TRACEPARENT})
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["traceId"] == TRACE_ID
