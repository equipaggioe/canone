"""The connections of the WebSocket, and what reaches each one."""

import asyncio
import contextlib
import json
import logging
from collections.abc import Coroutine
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import WebSocket
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from valkey.asyncio.client import PubSub
from valkey.exceptions import ValkeyError

from app import errors, ijson, store
from app.database import SessionFactory
from app.enums import EventLevel, SessionKind
from app.errors import Problem
from app.models.account.account import Account
from app.models.account.account_session import AccountSession
from app.schemas.base import InputSchema
from app.schemas.websocket import CLIENT, AccessTokenMessage, ErrorMessage, MessageProblem
from app.services import channel, events, limits, sessions
from app.services.limits import Rule
from app.services.sessions import Client, Principal

logger = logging.getLogger(__name__)

# The close codes: those of RFC 6455 and its registry, and the private
# one of a session that ended.
BINARY, POLICY, FAILED, RESTART, SLOW = 1003, 1008, 1011, 1012, 1013
UNAUTHENTICATED = 4401
CONNECTIONS = 10
MESSAGES = 100
MINUTE = timedelta(minutes=1)
# What a connection may have left to send.
PENDING = 100
# The place of a connection: whoever dies frees it by not renewing it.
PLACE = timedelta(seconds=60)
RENEWAL = timedelta(seconds=30)
RETRY = timedelta(seconds=30)
# How long each read of the subscription waits, in seconds: a silent
# one is not lost.
SILENCE = 30

# A sorted set keeps until when each place is taken.
TAKE = store.client.register_script("""
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
if redis.call('ZCARD', KEYS[1]) >= tonumber(ARGV[3]) then return 0 end
redis.call('ZADD', KEYS[1], ARGV[2], ARGV[4])
redis.call('PEXPIRE', KEYS[1], ARGV[5])
return 1
""")


class Refused(Exception):
    """A message the server does not take, and the errors it has."""

    def __init__(self, found: list[dict[str, Any]]) -> None:
        """Keep the errors, as Pydantic writes them."""
        super().__init__()
        self.found = found


class Connection:
    """An open connection of a session, and why it ends."""

    def __init__(self, row: AccountSession) -> None:
        """Start a connection that has nothing to send."""
        self.account_id = row.account_id
        self.session_id = row.id
        self.kind = row.kind
        self.deadline = row.token_expires_at or row.last_used_at + sessions.IDLE
        self.renewed = asyncio.Event()
        self.ended = asyncio.Event()
        self.code = 0
        self.outbox: asyncio.Queue[str] = asyncio.Queue(PENDING)

    def end(self, code: int) -> None:
        """End the connection; the first reason stays."""
        if not self.ended.is_set():
            self.code = code
            self.ended.set()

    def put(self, text: str) -> None:
        """Queue a message, or end a connection too slow to take it."""
        try:
            self.outbox.put_nowait(text)
        except asyncio.QueueFull:
            self.end(SLOW)


class Hub:
    """The connections of this process, over one subscription."""

    def __init__(self) -> None:
        """Start without connections, and without a subscription."""
        self.lock = asyncio.Lock()
        self.reset()

    def reset(self) -> None:
        """Forget the connections and the subscription."""
        self.members: dict[UUID, set[Connection]] = {}
        self.ready: dict[UUID, asyncio.Event] = {}
        self.pubsub: PubSub | None = None
        self.reader: asyncio.Task[None] | None = None

    async def join(self, connection: Connection) -> None:
        """Add a connection, once its channel is subscribed."""
        account_id = connection.account_id
        async with self.lock:
            pubsub = self.pubsub or store.client.pubsub()
            self.pubsub = pubsub
            self.members.setdefault(account_id, set()).add(connection)
            if account_id not in self.ready:
                self.ready[account_id] = asyncio.Event()
                await pubsub.subscribe(channel.name(account_id))
            ready = self.ready[account_id]
            if self.reader is None:
                self.reader = asyncio.create_task(self.read(pubsub))
        await ready.wait()

    async def leave(self, connection: Connection) -> None:
        """Remove a connection, and the subscription it leaves alone."""
        account_id = connection.account_id
        async with self.lock:
            group = self.members.get(account_id, set())
            # The subscription it joined may be lost already.
            if connection not in group or self.pubsub is None:
                return
            group.discard(connection)
            if group:
                return
            del self.members[account_id]
            self.ready.pop(account_id, None)
            if self.members:
                await self.pubsub.unsubscribe(channel.name(account_id))
                return
            pubsub, reader = self.pubsub, self.reader
            self.reset()
            if reader is not None:
                reader.cancel()
                await asyncio.gather(reader, return_exceptions=True)
            await pubsub.aclose()

    async def read(self, pubsub: PubSub) -> None:
        """Hand each message to its connections, until it is lost.

        What was published meanwhile does not come back, like the close
        of a session: every connection ends, and authenticates again.
        """
        try:
            while True:
                # listen() gives up after the socket timeout.
                message = await pubsub.get_message(timeout=SILENCE)
                if message is None:
                    continue
                name, data = message["channel"], message["data"]
                assert isinstance(name, bytes)
                account_id = UUID(name.decode().partition(":")[2])
                if message["type"] == "subscribe" and account_id in self.ready:
                    self.ready[account_id].set()
                elif message["type"] == "message":
                    assert isinstance(data, bytes)
                    self.dispatch(account_id, json.loads(data))
        except (ValkeyError, OSError):
            logger.exception("The subscription to Valkey was lost")
            self.lose()

    def lose(self) -> None:
        """End every connection, and start over with the next one."""
        members, ready = self.members, self.ready
        self.reset()
        for group in members.values():
            for connection in group:
                connection.end(RESTART)
        for event in ready.values():
            event.set()

    def dispatch(self, account_id: UUID, payload: dict[str, Any]) -> None:
        """Close the connections of a session, or send a message."""
        for connection in self.members.get(account_id, set()):
            if "close" not in payload:
                connection.put(json.dumps(payload["message"]))
            elif str(connection.session_id) in payload["close"]:
                connection.end(UNAUTHENTICATED)


hub = Hub()


def place_key(account_id: UUID) -> str:
    """Name the places of the connections of an account."""
    return f"websocket:places:{account_id}"


def until() -> int:
    """Return until when a place is taken, in milliseconds."""
    return limits.now() + limits.milliseconds(PLACE)


async def take_place(account_id: UUID, place: str, caller: Client) -> None:
    """Take a place of the account, or answer 429."""
    args = [limits.now(), until(), CONNECTIONS, place, limits.milliseconds(PLACE)]
    if await TAKE(keys=[place_key(account_id)], args=args):
        return
    await events.record(
        events.event(
            "excess_rate_limit_exceeded",
            EventLevel.WARN,
            actor_id=account_id,
            ip_address=caller.ip_address,
            user_agent=caller.user_agent,
            details={"max": CONNECTIONS},
        )
    )
    raise limits.too_many(limits.milliseconds(RETRY), "Ten open connections of this account")


async def serve(socket: WebSocket, principal: Principal, caller: Client) -> None:
    """Run the connection of a session, from its place to its end."""
    connection = Connection(principal.session)
    key, place = place_key(connection.account_id), uuid4().hex
    await take_place(connection.account_id, place, caller)
    try:
        await hub.join(connection)
        # Closed after the handshake read it, and before the channel.
        if await last_use(connection) is None:
            connection.end(UNAUTHENTICATED)
        await socket.accept()
        await run(socket, connection, place, caller)
    finally:
        with contextlib.suppress(ValkeyError, OSError):
            await hub.leave(connection)
            await store.client.zrem(key, place)


async def last_use(connection: Connection) -> datetime | None:
    """Return the last use of the session, or none if it ended."""
    async with SessionFactory() as session:
        row = await session.get(AccountSession, connection.session_id)
        account = await session.get(Account, connection.account_id)
    if row is None or account is None or account.disabled_at is not None:
        return None
    return row.last_used_at


async def run(socket: WebSocket, connection: Connection, place: str, caller: Client) -> None:
    """Listen until the TCP ends, with the tasks that serve it.

    A connection that stopped reading keeps its place until then.
    """
    sender = asyncio.create_task(guard(connection, send(socket, connection)))
    tasks = [
        sender,
        asyncio.create_task(guard(connection, keep(connection, place))),
        asyncio.create_task(guard(connection, watch(connection))),
        asyncio.create_task(finish(socket, connection, sender)),
    ]
    try:
        await listen(socket, connection, caller)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def guard(connection: Connection, work: Coroutine[Any, Any, None]) -> None:
    """Run a task of a connection; its failure ends the connection."""
    try:
        await work
    except (ValkeyError, OSError):
        logger.exception("A connection lost Valkey")
        connection.end(RESTART)
    except Exception:
        logger.exception("A task of a connection failed")
        connection.end(FAILED)


async def send(socket: WebSocket, connection: Connection) -> None:
    """Send what the connection has queued."""
    while True:
        await socket.send_text(await connection.outbox.get())


async def keep(connection: Connection, place: str) -> None:
    """Renew the place of the connection."""
    key = place_key(connection.account_id)
    while True:
        await asyncio.sleep(RENEWAL.total_seconds())
        async with store.client.pipeline(transaction=True) as pipe:
            pipe.zadd(key, {place: until()})
            pipe.pexpire(key, limits.milliseconds(PLACE))
            await pipe.execute()


async def watch(connection: Connection) -> None:
    """End the connection when its token or its session expires.

    The web may have used its session meanwhile: its row tells.
    """
    while True:
        left = (connection.deadline - datetime.now(UTC)).total_seconds()
        try:
            async with asyncio.timeout(max(left, 0)):
                await connection.renewed.wait()
            connection.renewed.clear()
            continue
        except TimeoutError:
            pass
        if connection.kind == SessionKind.WEB:
            used = await last_use(connection)
            if used is not None and used + sessions.IDLE > datetime.now(UTC):
                connection.deadline = used + sessions.IDLE
                continue
        connection.end(UNAUTHENTICATED)
        return


async def finish(socket: WebSocket, connection: Connection, sender: asyncio.Task[None]) -> None:
    """Close the connection with the code it ended with."""
    await connection.ended.wait()
    sender.cancel()
    await asyncio.gather(sender, return_exceptions=True)
    # The client may have gone first.
    with contextlib.suppress(RuntimeError, OSError):
        await socket.close(connection.code)


async def listen(socket: WebSocket, connection: Connection, caller: Client) -> None:
    """Take each message until the client is gone.

    One that fails goes to the log, and the app goes on.
    """
    while True:
        message = await socket.receive()
        if message["type"] == "websocket.disconnect":
            return
        if connection.ended.is_set():
            continue
        try:
            await take(connection, message.get("text"), caller)
        except Exception:
            logger.exception("A message failed")
            refuse(connection, errors.blank(500))


def refuse(connection: Connection, problem: Problem) -> None:
    """Tell the client why its message was not taken."""
    answer = ErrorMessage(data=MessageProblem.model_validate(problem))
    connection.put(answer.model_dump_json(exclude_none=True))


async def take(connection: Connection, text: str | None, caller: Client) -> None:
    """Take a message of the client, or tell it why not."""
    if text is None:
        connection.end(BINARY)
        return
    rule = Rule(
        f"websocket:messages:{connection.account_id}",
        MESSAGES,
        MINUTE,
        "A hundred messages a minute of this account",
    )
    try:
        await limits.take(caller, rule)
    except HTTPException:
        connection.end(POLICY)
        return
    try:
        message = parse(text)
    except Refused as refused:
        problem = await errors.invalid(refused.found, caller.ip_address, caller.user_agent)
        refuse(connection, problem)
        return
    await handle(connection, message, caller)


def parse(text: str) -> InputSchema:
    """Read a message of the client with the schema of its type."""
    found = ijson.problem(text.encode())
    if found is not None:
        raise Refused([{"type": found[0], "loc": ("body",), "msg": found[1]}])
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise Refused([{"type": "json_invalid", "loc": ("body",), "msg": str(error)}]) from error
    if not isinstance(value, dict):
        raise Refused([{"type": "dict_type", "loc": ("body",), "msg": "Not an object"}])
    schema = CLIENT.get(str(value.get("type")))
    if schema is None:
        raise Refused([{"type": "enum", "loc": ("body", "type"), "msg": "Not a message type"}])
    try:
        return schema.model_validate(value)
    except ValidationError as error:
        raise Refused(
            [
                {"type": item["type"], "loc": ("body", *item["loc"]), "msg": item["msg"]}
                for item in error.errors()
            ]
        ) from error


async def handle(connection: Connection, message: InputSchema, caller: Client) -> None:
    """Do what a message asks, if its account may."""
    if isinstance(message, AccessTokenMessage):
        await renew(connection, message.data.access_token, caller)


async def renew(connection: Connection, token: str, caller: Client) -> None:
    """Keep the connection until its new token expires.

    A token that does not hold, or of another session, ends it.
    """
    async with SessionFactory.begin() as session:
        principal = await sessions.resolve(session, token, SessionKind.APP, caller)
    expires = principal.session.token_expires_at if principal else None
    if principal is None or expires is None or principal.session.id != connection.session_id:
        connection.end(UNAUTHENTICATED)
        return
    connection.deadline = expires
    connection.renewed.set()
