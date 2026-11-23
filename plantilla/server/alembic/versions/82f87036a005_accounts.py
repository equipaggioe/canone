"""The accounts, their passwords and their sessions.

Revision ID: 82f87036a005
Revises: d34c1b992b0b
Create Date: 2026-11-22 23:35:53.199601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '82f87036a005'
down_revision: Union[str, Sequence[str], None] = 'd34c1b992b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The role of the server, named as the app.
ROLE = "PRODUCTO"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "account",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.TEXT(), nullable=True),
        sa.Column("phone", sa.TEXT(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name=op.f("ck_account_identified")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account")),
        sa.UniqueConstraint("email", name=op.f("uq_account_email")),
        sa.UniqueConstraint("phone", name=op.f("uq_account_phone")),
    )
    op.create_table(
        "account_session",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.TEXT(), nullable=False),
        sa.Column("token_digest", sa.LargeBinary(), nullable=False),
        sa.Column("token_expires_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("secret_digest", sa.LargeBinary(), nullable=True),
        sa.Column("previous_digest", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("kind IN ('web', 'app')", name=op.f("ck_account_session_sessionkind")),
        sa.CheckConstraint(
            "(kind = 'web' AND token_expires_at IS NULL AND secret_digest IS NULL AND previous_digest IS NULL)"
            " OR (kind = 'app' AND token_expires_at IS NOT NULL AND secret_digest IS NOT NULL)",
            name=op.f("ck_account_session_presentation"),
        ),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_account_session_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account_session")),
        sa.UniqueConstraint("token_digest", name=op.f("uq_account_session_token_digest")),
    )
    op.create_index(op.f("ix_account_session_account_id"), "account_session", ["account_id"])
    op.create_index(op.f("ix_account_session_last_used_at"), "account_session", ["last_used_at"])
    op.create_table(
        "password",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("hash", sa.TEXT(), nullable=False),
        sa.Column("failures", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("disabled_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_password_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", name=op.f("pk_password")),
    )
    op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON account, account_session, password TO {ROLE}")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("password")
    op.drop_index(op.f("ix_account_session_last_used_at"), table_name="account_session")
    op.drop_index(op.f("ix_account_session_account_id"), table_name="account_session")
    op.drop_table("account_session")
    op.drop_table("account")
