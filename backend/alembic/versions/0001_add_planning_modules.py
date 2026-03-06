"""add planning modules and bootstrap core schema

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


def _has_fk(inspector, table_name: str, fk_name: str) -> bool:
    if not _has_table(inspector, table_name):
        return False
    return any(fk["name"] == fk_name for fk in inspector.get_foreign_keys(table_name))


def _create_core_tables_if_missing(inspector) -> None:
    if not _has_table(inspector, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email", name="uq_users_email"),
        )
    if not _has_index(inspector, "users", "ix_users_id"):
        op.create_index("ix_users_id", "users", ["id"], unique=False)
    if not _has_index(inspector, "users", "ix_users_email"):
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if not _has_table(inspector, "groups"):
        op.create_table(
            "groups",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("join_code", sa.String(length=12), nullable=False),
            sa.Column("created_by", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_groups_created_by_users"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("join_code", name="uq_groups_join_code"),
        )
    if not _has_index(inspector, "groups", "ix_groups_id"):
        op.create_index("ix_groups_id", "groups", ["id"], unique=False)
    if not _has_index(inspector, "groups", "ix_groups_join_code"):
        op.create_index("ix_groups_join_code", "groups", ["join_code"], unique=True)

    if not _has_table(inspector, "memberships"):
        op.create_table(
            "memberships",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False, server_default="MEMBER"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
            sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "group_id", name="uq_user_group"),
        )
    if not _has_index(inspector, "memberships", "ix_memberships_id"):
        op.create_index("ix_memberships_id", "memberships", ["id"], unique=False)

    if not _has_table(inspector, "preferences"):
        op.create_table(
            "preferences",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("destination_type", sa.String(length=50), nullable=True),
            sa.Column("budget_min", sa.Integer(), nullable=True),
            sa.Column("budget_max", sa.Integer(), nullable=True),
            sa.Column("days", sa.Integer(), nullable=True),
            sa.Column("activities", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("transport_mode", sa.String(length=40), nullable=True),
            sa.Column("dietary_preferences", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("travel_pace", sa.String(length=30), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(inspector, "preferences", "ix_preferences_id"):
        op.create_index("ix_preferences_id", "preferences", ["id"], unique=False)
    if not _has_index(inspector, "preferences", "ix_preferences_group_id"):
        op.create_index("ix_preferences_group_id", "preferences", ["group_id"], unique=False)
    if not _has_index(inspector, "preferences", "ix_preferences_user_id"):
        op.create_index("ix_preferences_user_id", "preferences", ["user_id"], unique=False)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    _create_core_tables_if_missing(inspector)
    inspector = sa.inspect(bind)

    if not _has_column(inspector, "groups", "created_by"):
        op.add_column("groups", sa.Column("created_by", sa.Integer(), nullable=True))
    if not _has_column(inspector, "groups", "created_at"):
        op.add_column(
            "groups",
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
    if _has_column(inspector, "groups", "created_by") and not _has_fk(inspector, "groups", "fk_groups_created_by_users"):
        op.create_foreign_key("fk_groups_created_by_users", "groups", "users", ["created_by"], ["id"])

    if _has_table(inspector, "memberships") and not _has_column(inspector, "memberships", "status"):
        op.add_column(
            "memberships",
            sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        )

    if not _has_table(inspector, "catalog_items"):
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
    if not _has_index(inspector, "catalog_items", op.f("ix_catalog_items_id")):
        op.create_index(op.f("ix_catalog_items_id"), "catalog_items", ["id"], unique=False)

    if not _has_table(inspector, "itineraries"):
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
    if not _has_index(inspector, "itineraries", op.f("ix_itineraries_id")):
        op.create_index(op.f("ix_itineraries_id"), "itineraries", ["id"], unique=False)
    if not _has_index(inspector, "itineraries", op.f("ix_itineraries_group_id")):
        op.create_index(op.f("ix_itineraries_group_id"), "itineraries", ["group_id"], unique=False)

    if not _has_table(inspector, "itinerary_days"):
        op.create_table(
            "itinerary_days",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("itinerary_id", sa.Integer(), nullable=False),
            sa.Column("day_number", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["itinerary_id"], ["itineraries.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(inspector, "itinerary_days", op.f("ix_itinerary_days_id")):
        op.create_index(op.f("ix_itinerary_days_id"), "itinerary_days", ["id"], unique=False)
    if not _has_index(inspector, "itinerary_days", op.f("ix_itinerary_days_itinerary_id")):
        op.create_index(op.f("ix_itinerary_days_itinerary_id"), "itinerary_days", ["itinerary_id"], unique=False)

    if not _has_table(inspector, "itinerary_items"):
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
    if not _has_index(inspector, "itinerary_items", op.f("ix_itinerary_items_id")):
        op.create_index(op.f("ix_itinerary_items_id"), "itinerary_items", ["id"], unique=False)
    if not _has_index(inspector, "itinerary_items", op.f("ix_itinerary_items_itinerary_day_id")):
        op.create_index(op.f("ix_itinerary_items_itinerary_day_id"), "itinerary_items", ["itinerary_day_id"], unique=False)

    if not _has_table(inspector, "votes"):
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
    if not _has_index(inspector, "votes", op.f("ix_votes_id")):
        op.create_index(op.f("ix_votes_id"), "votes", ["id"], unique=False)
    if not _has_index(inspector, "votes", op.f("ix_votes_group_id")):
        op.create_index(op.f("ix_votes_group_id"), "votes", ["group_id"], unique=False)
    if not _has_index(inspector, "votes", op.f("ix_votes_itinerary_id")):
        op.create_index(op.f("ix_votes_itinerary_id"), "votes", ["itinerary_id"], unique=False)
    if not _has_index(inspector, "votes", op.f("ix_votes_user_id")):
        op.create_index(op.f("ix_votes_user_id"), "votes", ["user_id"], unique=False)

    if not _has_table(inspector, "notifications"):
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
    if not _has_index(inspector, "notifications", op.f("ix_notifications_id")):
        op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    if not _has_index(inspector, "notifications", op.f("ix_notifications_group_id")):
        op.create_index(op.f("ix_notifications_group_id"), "notifications", ["group_id"], unique=False)
    if not _has_index(inspector, "notifications", op.f("ix_notifications_user_id")):
        op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    if not _has_table(inspector, "invites"):
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
    if not _has_index(inspector, "invites", op.f("ix_invites_id")):
        op.create_index(op.f("ix_invites_id"), "invites", ["id"], unique=False)
    if not _has_index(inspector, "invites", op.f("ix_invites_group_id")):
        op.create_index(op.f("ix_invites_group_id"), "invites", ["group_id"], unique=False)
    if not _has_index(inspector, "invites", op.f("ix_invites_inviter_user_id")):
        op.create_index(op.f("ix_invites_inviter_user_id"), "invites", ["inviter_user_id"], unique=False)
    if not _has_index(inspector, "invites", op.f("ix_invites_email")):
        op.create_index(op.f("ix_invites_email"), "invites", ["email"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_index(inspector, "invites", op.f("ix_invites_email")):
        op.drop_index(op.f("ix_invites_email"), table_name="invites")
    if _has_index(inspector, "invites", op.f("ix_invites_inviter_user_id")):
        op.drop_index(op.f("ix_invites_inviter_user_id"), table_name="invites")
    if _has_index(inspector, "invites", op.f("ix_invites_group_id")):
        op.drop_index(op.f("ix_invites_group_id"), table_name="invites")
    if _has_index(inspector, "invites", op.f("ix_invites_id")):
        op.drop_index(op.f("ix_invites_id"), table_name="invites")
    if _has_table(inspector, "invites"):
        op.drop_table("invites")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "notifications", op.f("ix_notifications_user_id")):
        op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    if _has_index(inspector, "notifications", op.f("ix_notifications_group_id")):
        op.drop_index(op.f("ix_notifications_group_id"), table_name="notifications")
    if _has_index(inspector, "notifications", op.f("ix_notifications_id")):
        op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    if _has_table(inspector, "notifications"):
        op.drop_table("notifications")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "votes", op.f("ix_votes_user_id")):
        op.drop_index(op.f("ix_votes_user_id"), table_name="votes")
    if _has_index(inspector, "votes", op.f("ix_votes_itinerary_id")):
        op.drop_index(op.f("ix_votes_itinerary_id"), table_name="votes")
    if _has_index(inspector, "votes", op.f("ix_votes_group_id")):
        op.drop_index(op.f("ix_votes_group_id"), table_name="votes")
    if _has_index(inspector, "votes", op.f("ix_votes_id")):
        op.drop_index(op.f("ix_votes_id"), table_name="votes")
    if _has_table(inspector, "votes"):
        op.drop_table("votes")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "itinerary_items", op.f("ix_itinerary_items_itinerary_day_id")):
        op.drop_index(op.f("ix_itinerary_items_itinerary_day_id"), table_name="itinerary_items")
    if _has_index(inspector, "itinerary_items", op.f("ix_itinerary_items_id")):
        op.drop_index(op.f("ix_itinerary_items_id"), table_name="itinerary_items")
    if _has_table(inspector, "itinerary_items"):
        op.drop_table("itinerary_items")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "itinerary_days", op.f("ix_itinerary_days_itinerary_id")):
        op.drop_index(op.f("ix_itinerary_days_itinerary_id"), table_name="itinerary_days")
    if _has_index(inspector, "itinerary_days", op.f("ix_itinerary_days_id")):
        op.drop_index(op.f("ix_itinerary_days_id"), table_name="itinerary_days")
    if _has_table(inspector, "itinerary_days"):
        op.drop_table("itinerary_days")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "itineraries", op.f("ix_itineraries_group_id")):
        op.drop_index(op.f("ix_itineraries_group_id"), table_name="itineraries")
    if _has_index(inspector, "itineraries", op.f("ix_itineraries_id")):
        op.drop_index(op.f("ix_itineraries_id"), table_name="itineraries")
    if _has_table(inspector, "itineraries"):
        op.drop_table("itineraries")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "catalog_items", op.f("ix_catalog_items_id")):
        op.drop_index(op.f("ix_catalog_items_id"), table_name="catalog_items")
    if _has_table(inspector, "catalog_items"):
        op.drop_table("catalog_items")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "preferences", "ix_preferences_group_id"):
        op.drop_index("ix_preferences_group_id", table_name="preferences")
    if _has_index(inspector, "preferences", "ix_preferences_user_id"):
        op.drop_index("ix_preferences_user_id", table_name="preferences")
    if _has_index(inspector, "preferences", "ix_preferences_id"):
        op.drop_index("ix_preferences_id", table_name="preferences")
    if _has_table(inspector, "preferences"):
        op.drop_table("preferences")

    inspector = sa.inspect(bind)
    if _has_column(inspector, "memberships", "status"):
        op.drop_column("memberships", "status")
    if _has_fk(inspector, "groups", "fk_groups_created_by_users"):
        op.drop_constraint("fk_groups_created_by_users", "groups", type_="foreignkey")
    if _has_column(inspector, "groups", "created_at"):
        op.drop_column("groups", "created_at")
    if _has_column(inspector, "groups", "created_by"):
        op.drop_column("groups", "created_by")

    inspector = sa.inspect(bind)
    if _has_index(inspector, "memberships", "ix_memberships_id"):
        op.drop_index("ix_memberships_id", table_name="memberships")
    if _has_table(inspector, "memberships"):
        op.drop_table("memberships")
    if _has_index(inspector, "groups", "ix_groups_join_code"):
        op.drop_index("ix_groups_join_code", table_name="groups")
    if _has_index(inspector, "groups", "ix_groups_id"):
        op.drop_index("ix_groups_id", table_name="groups")
    if _has_table(inspector, "groups"):
        op.drop_table("groups")
    if _has_index(inspector, "users", "ix_users_email"):
        op.drop_index("ix_users_email", table_name="users")
    if _has_index(inspector, "users", "ix_users_id"):
        op.drop_index("ix_users_id", table_name="users")
    if _has_table(inspector, "users"):
        op.drop_table("users")
