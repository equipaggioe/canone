"""Rate limits over a sliding window, and blocks, in Valkey."""

import math
import secrets
import time
from dataclasses import dataclass
from datetime import timedelta
from http import HTTPStatus

from fastapi import HTTPException

from app import store
from app.enums import EventLevel
from app.services import events
from app.services.sessions import Client

# Each key keeps the moments of its hits in a sorted set. A hit counts
# on every rule only if none is full; if one is, the script answers the
# milliseconds until it frees and its position.
TAKE = store.client.register_script("""
local now = tonumber(ARGV[1])
local wait, full = 0, 0
for i, key in ipairs(KEYS) do
  local limit = tonumber(ARGV[1 + i * 2])
  local window = tonumber(ARGV[2 + i * 2])
  redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
  local count = redis.call('ZCARD', key)
  if count >= limit then
    local oldest = redis.call('ZRANGE', key, count - limit, count - limit, 'WITHSCORES')
    local free = tonumber(oldest[2]) + window - now
    if free > wait then wait, full = free, i end
  end
end
if full > 0 then return {wait, full} end
for i, key in ipairs(KEYS) do
  redis.call('ZADD', key, now, ARGV[2])
  redis.call('PEXPIRE', key, tonumber(ARGV[2 + i * 2]))
end
return {0, 0}
""")


@dataclass(frozen=True)
class Rule:
    """At most limit hits of a key within a window."""

    key: str
    limit: int
    window: timedelta
    # fastapi.md: the detail of a 429 says which limit was passed.
    detail: str


def now() -> int:
    """Return the time in milliseconds."""
    return time.time_ns() // 1_000_000


def milliseconds(span: timedelta) -> int:
    """Write a span in milliseconds."""
    return int(span.total_seconds() * 1000)


def too_many(wait: int, detail: str) -> HTTPException:
    """Answer 429, with the seconds until the limit frees."""
    seconds = max(1, math.ceil(wait / 1000))
    return HTTPException(
        HTTPStatus.TOO_MANY_REQUESTS, detail, headers={"Retry-After": str(seconds)}
    )


async def take(client: Client, *rules: Rule) -> None:
    """Count a hit on each rule, or answer 429 if one is full."""
    args: list[int | str] = [now(), secrets.token_hex(8)]
    for rule in rules:
        args += [rule.limit, milliseconds(rule.window)]
    keys = [f"limit:{rule.key}" for rule in rules]
    wait, full = (int(value) for value in await TAKE(keys=keys, args=args))
    if not full:
        return
    rule = rules[full - 1]
    await events.record(
        events.event(
            "excess_rate_limit_exceeded",
            EventLevel.WARN,
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            details={"max": rule.limit},
        )
    )
    raise too_many(wait, rule.detail)


async def hit(rule: Rule) -> bool:
    """Count a hit that is never refused; tell whether it filled."""
    key = f"limit:{rule.key}"
    moment = now()
    async with store.client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, "-inf", moment - milliseconds(rule.window))
        pipe.zadd(key, {secrets.token_hex(8): moment})
        pipe.zcard(key)
        pipe.pexpire(key, milliseconds(rule.window))
        count = (await pipe.execute())[2]
    assert isinstance(count, int)
    return count >= rule.limit


async def block(key: str, span: timedelta) -> None:
    """Block a key for a span."""
    await store.client.set(f"block:{key}", b"", px=milliseconds(span))


async def check_block(key: str, detail: str) -> None:
    """Answer 429 while a key is blocked."""
    left = await store.client.pttl(f"block:{key}")
    if left > 0:
        raise too_many(left, detail)
