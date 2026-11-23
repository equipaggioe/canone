"""The consecutive failures of an authenticator, and its waits."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


class Throttled:
    """An authenticator that waits and disables by its failures."""

    failures: Mapped[int] = mapped_column(server_default=sa.text("0"))
    # The earliest time of the next attempt, from the fifth failure.
    retry_at: Mapped[datetime | None]
    disabled_at: Mapped[datetime | None]
