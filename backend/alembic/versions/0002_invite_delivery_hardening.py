"""add invite delivery tracking and webhook support fields

Revision ID: 0002_invite_delivery_hardening
Revises: 0001_add_planning_modules
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_invite_delivery_hardening"
down_revision = "0001_add_planning_modules"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    if not _has_table(inspector, table_name):
        return False
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    if not _has_table(inspector, table_name):
        return False
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, "invites") and not _has_column(inspector, "invites", "delivery_status"):
        op.add_column("invites", sa.Column("delivery_status", sa.String(length=20), nullable=False, server_default="PENDING"))
    if _has_table(inspector, "invites") and not _has_column(inspector, "invites", "delivery_provider"):
        op.add_column("invites", sa.Column("delivery_provider", sa.String(length=40), nullable=True))
    if _has_table(inspector, "invites") and not _has_column(inspector, "invites", "delivery_provider_id"):
        op.add_column("invites", sa.Column("delivery_provider_id", sa.String(length=128), nullable=True))
    if _has_table(inspector, "invites") and not _has_column(inspector, "invites", "delivery_attempts"):
        op.add_column("invites", sa.Column("delivery_attempts", sa.Integer(), nullable=False, server_default="0"))
    if _has_table(inspector, "invites") and not _has_column(inspector, "invites", "delivery_last_error"):
        op.add_column("invites", sa.Column("delivery_last_error", sa.String(length=500), nullable=True))
    if _has_table(inspector, "invites") and not _has_column(inspector, "invites", "delivery_last_attempt_at"):
        op.add_column("invites", sa.Column("delivery_last_attempt_at", sa.DateTime(timezone=True), nullable=True))

    inspector = sa.inspect(bind)
    if not _has_table(inspector, "invite_delivery_attempts"):
        op.create_table(
            "invite_delivery_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("invite_id", sa.Integer(), nullable=False),
            sa.Column("attempt_number", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("provider_message_id", sa.String(length=128), nullable=True),
            sa.Column("error_message", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["invite_id"], ["invites.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(inspector, "invite_delivery_attempts", op.f("ix_invite_delivery_attempts_id")):
        op.create_index(op.f("ix_invite_delivery_attempts_id"), "invite_delivery_attempts", ["id"], unique=False)
    if not _has_index(inspector, "invite_delivery_attempts", op.f("ix_invite_delivery_attempts_invite_id")):
        op.create_index(op.f("ix_invite_delivery_attempts_invite_id"), "invite_delivery_attempts", ["invite_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_index(inspector, "invite_delivery_attempts", op.f("ix_invite_delivery_attempts_invite_id")):
        op.drop_index(op.f("ix_invite_delivery_attempts_invite_id"), table_name="invite_delivery_attempts")
    if _has_index(inspector, "invite_delivery_attempts", op.f("ix_invite_delivery_attempts_id")):
        op.drop_index(op.f("ix_invite_delivery_attempts_id"), table_name="invite_delivery_attempts")
    if _has_table(inspector, "invite_delivery_attempts"):
        op.drop_table("invite_delivery_attempts")

    inspector = sa.inspect(bind)
    if _has_column(inspector, "invites", "delivery_last_attempt_at"):
        op.drop_column("invites", "delivery_last_attempt_at")
    if _has_column(inspector, "invites", "delivery_last_error"):
        op.drop_column("invites", "delivery_last_error")
    if _has_column(inspector, "invites", "delivery_attempts"):
        op.drop_column("invites", "delivery_attempts")
    if _has_column(inspector, "invites", "delivery_provider_id"):
        op.drop_column("invites", "delivery_provider_id")
    if _has_column(inspector, "invites", "delivery_provider"):
        op.drop_column("invites", "delivery_provider")
    if _has_column(inspector, "invites", "delivery_status"):
        op.drop_column("invites", "delivery_status")
