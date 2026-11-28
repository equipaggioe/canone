"""Run a task of the machine: python -m app.tasks <task>."""

import argparse
import asyncio
import contextlib
import logging
import signal
from collections.abc import Awaitable, Callable

from opentelemetry import trace

from app import tracing
from app.database import engine, migrate, mock
from app.services import events, files, recovery, sessions, web_push

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


async def purge() -> None:
    """Delete the expired events and sessions."""
    await events.purge()
    await sessions.purge()


TASKS: dict[str, Callable[[], Awaitable[None]]] = {
    "migrate": migrate,
    "mock": mock,
    "purge": purge,
    "recover": recovery.apply_due,
    "sweep": files.sweep,
}
# fastapi.md: the calendar of each other task, as OnCalendar=.
TIMERS: dict[str, str] = {"recover": "minutely"}
# fastapi.md: each worker, with the seconds between its rounds.
WORKERS: dict[str, float] = {}


async def work(task: str) -> None:
    """Run the worker in rounds until SIGTERM, and log the failures."""
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    def ask(*_: object) -> None:
        """Let the round end, and start no other."""
        loop.call_soon_threadsafe(stop.set)

    # ADR-0252: systemd stops the worker between two rounds.
    previous = signal.signal(signal.SIGTERM, ask)
    try:
        while not stop.is_set():
            with tracer.start_as_current_span(task):
                # ADR-0251: a round that fails does not end the worker.
                try:
                    await TASKS[task]()
                except Exception:
                    logger.exception("A round of %s failed", task)
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), WORKERS[task])
    finally:
        signal.signal(signal.SIGTERM, previous)


async def run(task: str) -> None:
    """Run the task, or the worker, and close the connections."""
    try:
        if task in WORKERS:
            await work(task)
        else:
            with tracer.start_as_current_span(task):
                await TASKS[task]()
    finally:
        await engine.dispose()
        await web_push.client.aclose()


def main() -> None:
    """Read the task from the command line and run it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=TASKS)
    task = parser.parse_args().task
    tracing.install()
    asyncio.run(run(task))


if __name__ == "__main__":
    main()
