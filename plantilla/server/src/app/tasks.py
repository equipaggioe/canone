"""Run a task of the machine: python -m app.tasks <task>."""

import argparse
import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.database import engine, migrate, mock
from app.services import events, files, recovery, sessions, web_push

logger = logging.getLogger(__name__)


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
    """Run the worker in rounds, and log the round that fails."""
    while True:
        # ADR-0251: a round that fails does not end the worker.
        try:
            await TASKS[task]()
        except Exception:
            logger.exception("A round of %s failed", task)
        await asyncio.sleep(WORKERS[task])


async def run(task: str) -> None:
    """Run the task, or the worker, and close the connections."""
    try:
        await (work(task) if task in WORKERS else TASKS[task]())
    finally:
        await engine.dispose()
        await web_push.client.aclose()


def main() -> None:
    """Read the task from the command line and run it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=TASKS)
    asyncio.run(run(parser.parse_args().task))


if __name__ == "__main__":
    main()
