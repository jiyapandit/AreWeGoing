"""add group metric snapshots history table

Revision ID: 0003_group_metric_snapshots
Revises: 0002_invite_delivery_hardening
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_group_metric_snapshots"
down_revision = "0002_invite_delivery_hardening"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    if not _has_table(inspector, table_name):
        return False
    return any(idx["name"] == index_name for idx in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "group_metric_snapshots"):
        op.create_table(
            "group_metric_snapshots",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("captured_by", sa.Integer(), nullable=True),
            sa.Column("group_size", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("preference_completion_percent", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("budget_alignment_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activity_match_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("conflict_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("itinerary_confidence_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("approval_status", sa.String(length=60), nullable=False, server_default="NOT_STARTED"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["captured_by"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(inspector, "group_metric_snapshots", op.f("ix_group_metric_snapshots_id")):
        op.create_index(op.f("ix_group_metric_snapshots_id"), "group_metric_snapshots", ["id"], unique=False)
    if not _has_index(inspector, "group_metric_snapshots", op.f("ix_group_metric_snapshots_group_id")):
        op.create_index(op.f("ix_group_metric_snapshots_group_id"), "group_metric_snapshots", ["group_id"], unique=False)
    if not _has_index(inspector, "group_metric_snapshots", op.f("ix_group_metric_snapshots_captured_by")):
        op.create_index(op.f("ix_group_metric_snapshots_captured_by"), "group_metric_snapshots", ["captured_by"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_index(inspector, "group_metric_snapshots", op.f("ix_group_metric_snapshots_captured_by")):
        op.drop_index(op.f("ix_group_metric_snapshots_captured_by"), table_name="group_metric_snapshots")
    if _has_index(inspector, "group_metric_snapshots", op.f("ix_group_metric_snapshots_group_id")):
        op.drop_index(op.f("ix_group_metric_snapshots_group_id"), table_name="group_metric_snapshots")
    if _has_index(inspector, "group_metric_snapshots", op.f("ix_group_metric_snapshots_id")):
        op.drop_index(op.f("ix_group_metric_snapshots_id"), table_name="group_metric_snapshots")
    if _has_table(inspector, "group_metric_snapshots"):
        op.drop_table("group_metric_snapshots")
