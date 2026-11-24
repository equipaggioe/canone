"""A session of the web or of an app, one row per device."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import SessionKind
from app.models.base import Base, CreatedAt, UuidPk

# The web presents its cookie; an app, an access token that expires
# and the secret of its refresh token, current and previous.
PRESENTATION = "(kind = 'web' AND token_expires_at IS NULL AND secret_digest IS NULL AND previous_digest IS NULL) OR (kind = 'app' AND token_expires_at IS NOT NULL AND secret_digest IS NOT NULL)"


class AccountSession(Base):
    """What the web and the apps present; the SHA-256 of each token."""

    __tablename__ = "account_session"
    __table_args__ = (sa.CheckConstraint(PRESENTATION, name="presentation"),)

    id: Mapped[UuidPk]
    account_id: Mapped[UUID] = mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"), index=True)
    kind: Mapped[SessionKind]
    # The token of the web, or the access token of an app.
    token_digest: Mapped[bytes] = mapped_column(unique=True)
    token_expires_at: Mapped[datetime | None]
    secret_digest: Mapped[bytes | None]
    previous_digest: Mapped[bytes | None]
    created_at: Mapped[CreatedAt]
    # When the holder last proved who they are: signing in or again.
    authenticated_at: Mapped[datetime]
    last_used_at: Mapped[datetime] = mapped_column(server_default=sa.text("now()"), index=True)
