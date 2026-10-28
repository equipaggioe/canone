"""event_log, which the server only inserts and reads.

Revision ID: d34c1b992b0b
Revises:
Create Date: 2026-10-24 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd34c1b992b0b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The role of the server, named as the app.
ROLE = "PRODUCTO"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "event_log",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("occurred_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("action", sa.TEXT(), nullable=False),
        sa.Column("level", sa.TEXT(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("actor_label", sa.TEXT(), nullable=True),
        sa.Column("target_type", sa.TEXT(), nullable=True),
        sa.Column("target_id", sa.TEXT(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.TEXT(), nullable=True),
        sa.Column("trace_id", sa.TEXT(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.CheckConstraint("level IN ('info', 'warn', 'critical')", name=op.f("ck_event_log_eventlevel")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event_log")),
    )
    op.create_index(op.f("ix_event_log_occurred_at"), "event_log", ["occurred_at"])
    op.create_index("ix_event_log_critical", "event_log", ["occurred_at"], postgresql_where=sa.text("level = 'critical'"))
    # ADR-0100: SQLAlchemy has no xid8.
    op.execute("ALTER TABLE event_log ADD COLUMN xid xid8 NOT NULL DEFAULT pg_current_xact_id()")
    op.create_index("ix_event_log_xid", "event_log", ["xid", "id"])
    # The server cannot change or delete the trail.
    op.execute(f"GRANT INSERT, SELECT ON event_log TO {ROLE}")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_event_log_xid", table_name="event_log")
    op.drop_index("ix_event_log_critical", table_name="event_log", postgresql_where=sa.text("level = 'critical'"))
    op.drop_index(op.f("ix_event_log_occurred_at"), table_name="event_log")
    op.drop_table("event_log")
