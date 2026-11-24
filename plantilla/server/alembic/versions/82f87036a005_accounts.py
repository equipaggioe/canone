"""The accounts, their authenticators, their recovery and their sessions.

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
# ADR-0232: an account with a number has its row in phone, checked at the
# commit, when the registration or the change has written both.
PHONE_BOUND = (
    """
CREATE FUNCTION phone_bound() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    owner uuid;
BEGIN
    IF TG_TABLE_NAME = 'account' THEN
        owner := NEW.id;
    ELSE
        owner := OLD.account_id;
    END IF;
    IF EXISTS (
        SELECT FROM account
        WHERE id = owner AND phone IS NOT NULL
          AND NOT EXISTS (SELECT FROM phone WHERE phone.account_id = owner)
    ) THEN
        RAISE EXCEPTION 'account % has a phone without its row in phone', owner
            USING ERRCODE = 'integrity_constraint_violation';
    END IF;
    RETURN NULL;
END
$$
""",
    "CREATE CONSTRAINT TRIGGER account_phone_bound AFTER INSERT OR UPDATE OF phone ON account"
    " DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION phone_bound()",
    "CREATE CONSTRAINT TRIGGER phone_phone_bound AFTER DELETE ON phone"
    " DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION phone_bound()",
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "account",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.TEXT(), nullable=True),
        sa.Column("phone", sa.TEXT(), nullable=True),
        sa.Column("user_handle", sa.LargeBinary(), nullable=False),
        sa.Column("role", sa.TEXT(), nullable=False),
        sa.Column("language", sa.TEXT(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name=op.f("ck_account_identified")),
        sa.CheckConstraint("role IN ('superadmin', 'user')", name=op.f("ck_account_role")),
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
        sa.Column("authenticated_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
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
    op.create_table(
        "phone",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("failures", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("disabled_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_phone_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", name=op.f("pk_phone")),
    )
    op.create_table(
        "passkey",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("credential_id", sa.LargeBinary(), nullable=False),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.BigInteger(), nullable=False),
        sa.Column("uv_initialized", sa.Boolean(), nullable=False),
        sa.Column("transports", postgresql.ARRAY(sa.TEXT()), nullable=False),
        sa.Column("backup_eligible", sa.Boolean(), nullable=False),
        sa.Column("backup_state", sa.Boolean(), nullable=False),
        sa.Column("name", sa.TEXT(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("failures", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("disabled_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_passkey_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_passkey")),
        sa.UniqueConstraint("credential_id", name=op.f("uq_passkey_credential_id")),
    )
    op.create_index(op.f("ix_passkey_account_id"), "passkey", ["account_id"])
    op.create_table(
        "recovery",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("address", sa.TEXT(), nullable=False),
        sa.Column("applies_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("password_hash", sa.TEXT(), nullable=True),
        sa.Column("credential_id", sa.LargeBinary(), nullable=True),
        sa.Column("public_key", sa.LargeBinary(), nullable=True),
        sa.Column("sign_count", sa.BigInteger(), nullable=True),
        sa.Column("uv_initialized", sa.Boolean(), nullable=True),
        sa.Column("transports", postgresql.ARRAY(sa.TEXT()), nullable=True),
        sa.Column("backup_eligible", sa.Boolean(), nullable=True),
        sa.Column("backup_state", sa.Boolean(), nullable=True),
        sa.Column("passkey_name", sa.TEXT(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("address IN ('email', 'phone')", name=op.f("ck_recovery_address")),
        sa.CheckConstraint(
            "(password_hash IS NOT NULL AND credential_id IS NULL AND public_key IS NULL AND sign_count IS NULL"
            " AND uv_initialized IS NULL AND transports IS NULL AND backup_eligible IS NULL AND backup_state IS NULL"
            " AND passkey_name IS NULL) OR (password_hash IS NULL AND credential_id IS NOT NULL AND public_key IS NOT NULL"
            " AND sign_count IS NOT NULL AND uv_initialized IS NOT NULL AND transports IS NOT NULL"
            " AND backup_eligible IS NOT NULL AND backup_state IS NOT NULL AND passkey_name IS NOT NULL)",
            name=op.f("ck_recovery_authenticator"),
        ),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_recovery_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", name=op.f("pk_recovery")),
    )
    op.create_index(op.f("ix_recovery_applies_at"), "recovery", ["applies_at"])
    op.create_table(
        "recovery_address",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("address", sa.TEXT(), nullable=False),
        sa.Column("failures", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("disabled_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint("address IN ('email', 'phone')", name=op.f("ck_recovery_address_address")),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_recovery_address_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", "address", name=op.f("pk_recovery_address")),
    )
    op.create_table(
        "recovery_code",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("hash", sa.TEXT(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("failures", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("disabled_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["account.id"], name=op.f("fk_recovery_code_account_id_account"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", name=op.f("pk_recovery_code")),
    )
    for statement in PHONE_BOUND:
        op.execute(statement)
    op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON account, account_session, passkey, password, phone, recovery, recovery_address, recovery_code TO {ROLE}")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER phone_phone_bound ON phone")
    op.execute("DROP TRIGGER account_phone_bound ON account")
    op.execute("DROP FUNCTION phone_bound()")
    op.drop_table("recovery_code")
    op.drop_table("recovery_address")
    op.drop_index(op.f("ix_recovery_applies_at"), table_name="recovery")
    op.drop_table("recovery")
    op.drop_index(op.f("ix_passkey_account_id"), table_name="passkey")
    op.drop_table("passkey")
    op.drop_table("phone")
    op.drop_table("password")
    op.drop_index(op.f("ix_account_session_last_used_at"), table_name="account_session")
    op.drop_index(op.f("ix_account_session_account_id"), table_name="account_session")
    op.drop_table("account_session")
    op.drop_table("account")
