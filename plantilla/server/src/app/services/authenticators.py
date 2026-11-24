"""The waits and the limit of the failures of an authenticator."""

import math
from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi import HTTPException

from app.errors import AUTHENTICATOR_DISABLED, AppError
from app.models.account.throttled import Throttled
from app.models.event.event_log import EventLog
from app.services import events

WAIT_FROM = 5
FIRST_WAIT = timedelta(seconds=30)
LONGEST_WAIT = timedelta(hours=1)
# 30 seconds doubled 7 times passes the hour.
DOUBLINGS = 7
DISABLE_AT = 100


def wait(failures: int) -> timedelta | None:
    """Return how long the next attempt waits after failures."""
    if failures < WAIT_FROM:
        return None
    return min(FIRST_WAIT * 2 ** min(failures - WAIT_FROM, DOUBLINGS), LONGEST_WAIT)


async def admit(row: Throttled, now: datetime, early: EventLog) -> None:
    """Refuse an attempt on a disabled authenticator or before its wait.

    A refusal checks no credential, and an early attempt writes early.
    """
    if row.disabled_at is not None:
        raise AppError(AUTHENTICATOR_DISABLED)
    if row.retry_at is not None and now < row.retry_at:
        await events.record(early)
        seconds = math.ceil((row.retry_at - now).total_seconds())
        raise HTTPException(
            HTTPStatus.TOO_MANY_REQUESTS,
            "Too many failed attempts with this authenticator",
            headers={"Retry-After": str(seconds)},
        )


def fail(row: Throttled, now: datetime) -> bool:
    """Count a failure; tell whether it disabled the authenticator."""
    row.failures += 1
    delay = wait(row.failures)
    row.retry_at = now + delay if delay else None
    if row.failures >= DISABLE_AT:
        row.disabled_at = now
    return row.disabled_at is not None


def succeed(row: Throttled) -> int:
    """Reset the failures after a login, and return how many."""
    retries = row.failures
    row.failures = 0
    row.retry_at = None
    return retries


def enable(row: Throttled) -> None:
    """Enable a disabled authenticator again, with no failures."""
    row.failures = 0
    row.retry_at = None
    row.disabled_at = None
