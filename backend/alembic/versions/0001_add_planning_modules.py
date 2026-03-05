"""add planning modules

Revision ID: 0001_add_planning_modules
Revises:
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_add_planning_modules"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("created_by", sa.Integer(), nullable=True))
    op.add_column(
        "groups",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_foreign_key("fk_groups_created_by_users", "groups", "users", ["created_by"], ["id"])

    op.add_column(
        "memberships",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
    )

    op.create_table(
        "catalog_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.String(length=600), nullable=False),
        sa.Column("estimated_budget", sa.Integer(), nullable=False),
        sa.Column("duration_hours", sa.Float(), nullable=False),
        sa.Column("tags_csv", sa.String(length=300), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_catalog_items_id"), "catalog_items", ["id"], unique=False)

    op.create_table(
        "itineraries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="DRAFT"),
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_itineraries_id"), "itineraries", ["id"], unique=False)
    op.create_index(op.f("ix_itineraries_group_id"), "itineraries", ["group_id"], unique=False)

    op.create_table(
        "itinerary_days",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["itinerary_id"], ["itineraries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_itinerary_days_id"), "itinerary_days", ["id"], unique=False)
    op.create_index(op.f("ix_itinerary_days_itinerary_id"), "itinerary_days", ["itinerary_id"], unique=False)

    op.create_table(
        "itinerary_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("itinerary_day_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.String(length=600), nullable=False),
        sa.Column("estimated_cost", sa.Integer(), nullable=False),
        sa.Column("duration_hours", sa.Float(), nullable=False),
        sa.Column("rationale", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["itinerary_day_id"], ["itinerary_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_itinerary_items_id"), "itinerary_items", ["id"], unique=False)
    op.create_index(op.f("ix_itinerary_items_itinerary_day_id"), "itinerary_items", ["itinerary_day_id"], unique=False)

    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["itinerary_id"], ["itineraries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("itinerary_id", "user_id", name="uq_vote_itinerary_user"),
    )
    op.create_index(op.f("ix_votes_id"), "votes", ["id"], unique=False)
    op.create_index(op.f("ix_votes_group_id"), "votes", ["group_id"], unique=False)
    op.create_index(op.f("ix_votes_itinerary_id"), "votes", ["itinerary_id"], unique=False)
    op.create_index(op.f("ix_votes_user_id"), "votes", ["user_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_group_id"), "notifications", ["group_id"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    op.create_table(
        "invites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("inviter_user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="SENT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["inviter_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invites_id"), "invites", ["id"], unique=False)
    op.create_index(op.f("ix_invites_group_id"), "invites", ["group_id"], unique=False)
    op.create_index(op.f("ix_invites_inviter_user_id"), "invites", ["inviter_user_id"], unique=False)
    op.create_index(op.f("ix_invites_email"), "invites", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_invites_email"), table_name="invites")
    op.drop_index(op.f("ix_invites_inviter_user_id"), table_name="invites")
    op.drop_index(op.f("ix_invites_group_id"), table_name="invites")
    op.drop_index(op.f("ix_invites_id"), table_name="invites")
    op.drop_table("invites")

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_group_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_votes_user_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_itinerary_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_group_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_id"), table_name="votes")
    op.drop_table("votes")

    op.drop_index(op.f("ix_itinerary_items_itinerary_day_id"), table_name="itinerary_items")
    op.drop_index(op.f("ix_itinerary_items_id"), table_name="itinerary_items")
    op.drop_table("itinerary_items")

    op.drop_index(op.f("ix_itinerary_days_itinerary_id"), table_name="itinerary_days")
    op.drop_index(op.f("ix_itinerary_days_id"), table_name="itinerary_days")
    op.drop_table("itinerary_days")

    op.drop_index(op.f("ix_itineraries_group_id"), table_name="itineraries")
    op.drop_index(op.f("ix_itineraries_id"), table_name="itineraries")
    op.drop_table("itineraries")

    op.drop_index(op.f("ix_catalog_items_id"), table_name="catalog_items")
    op.drop_table("catalog_items")

    op.drop_column("memberships", "status")
    op.drop_constraint("fk_groups_created_by_users", "groups", type_="foreignkey")
    op.drop_column("groups", "created_at")
    op.drop_column("groups", "created_by")
