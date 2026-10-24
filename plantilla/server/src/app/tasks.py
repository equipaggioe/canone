"""Run a periodic task: python -m app.tasks <task>."""

import argparse
import asyncio
from collections.abc import Awaitable, Callable

from app.database import engine
from app.services import files

TASKS: dict[str, Callable[[], Awaitable[None]]] = {"sweep": files.sweep}


async def run(task: str) -> None:
    """Run the task, and close the pooled connections."""
    try:
        await TASKS[task]()
    finally:
        await engine.dispose()


def main() -> None:
    """Read the task from the command line and run it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=TASKS)
    asyncio.run(run(parser.parse_args().task))


if __name__ == "__main__":
    main()
