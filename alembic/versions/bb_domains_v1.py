"""add domain goals, checkins, progress log, and weekly snapshots

Revision ID: bb_domains_v1
Revises: <your_last_revision_id>   ← paste your current alembic head here
Create Date: 2026-03-21

Usage:
  1. alembic heads  → copy the ID shown → paste into down_revision below
  2. cp alembic_migration.py alembic/versions/bb_domains_v1.py
  3. alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa

revision = "bb_domains_v1"
down_revision = None   # ← set this
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── domain_goals ──────────────────────────────────────────────────────────
    op.create_table(
        "domain_goals",
        sa.Column("id",          sa.String(36),  primary_key=True),
        sa.Column("user_id",     sa.String(36),  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("domain_id",   sa.String(32),  nullable=False),
        sa.Column("title",       sa.String(255), nullable=False),
        sa.Column("description", sa.Text(),       nullable=True),
        sa.Column("category",    sa.String(64),  nullable=True),
        sa.Column("progress",    sa.Integer(),   server_default="0",      nullable=False),
        sa.Column("status",      sa.Enum("active", "completed", "paused", name="goal_status_enum"), server_default="active", nullable=False),
        sa.Column("target_date", sa.String(10),  nullable=True),
        sa.Column("created_at",  sa.DateTime(),  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",  sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_domain_goals_user_id",     "domain_goals", ["user_id"])
    op.create_index("ix_domain_goals_domain_id",   "domain_goals", ["domain_id"])
    op.create_index("ix_domain_goals_user_domain", "domain_goals", ["user_id", "domain_id"])

    # ── domain_checkins ───────────────────────────────────────────────────────
    op.create_table(
        "domain_checkins",
        sa.Column("id",         sa.String(36), primary_key=True),
        sa.Column("user_id",    sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("domain_id",  sa.String(32), nullable=False),
        sa.Column("date",       sa.String(10), nullable=False),
        sa.Column("status",     sa.Enum("completed", "partial", "missed", name="checkin_status_enum"), server_default="completed", nullable=False),
        sa.Column("notes",      sa.Text(),      nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_domain_checkins_user_id",   "domain_checkins", ["user_id"])
    op.create_index("ix_domain_checkins_domain_id", "domain_checkins", ["domain_id"])
    op.create_unique_constraint(
        "uq_checkin_user_domain_date", "domain_checkins",
        ["user_id", "domain_id", "date"],
    )

    # ── goal_progress_logs ────────────────────────────────────────────────────
    op.create_table(
        "goal_progress_logs",
        sa.Column("id",        sa.String(36), primary_key=True),
        sa.Column("goal_id",   sa.String(36), sa.ForeignKey("domain_goals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id",   sa.String(36), sa.ForeignKey("users.id",        ondelete="CASCADE"), nullable=False),
        sa.Column("progress",  sa.Integer(),  nullable=False),
        sa.Column("logged_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_goal_progress_logs_goal_id",   "goal_progress_logs", ["goal_id"])
    op.create_index("ix_goal_progress_logs_user_id",   "goal_progress_logs", ["user_id"])
    op.create_index("ix_goal_progress_logs_logged_at", "goal_progress_logs", ["logged_at"])

    # ── domain_weekly_snapshots ───────────────────────────────────────────────
    op.create_table(
        "domain_weekly_snapshots",
        sa.Column("id",              sa.String(36),  primary_key=True),
        sa.Column("user_id",         sa.String(36),  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("domain_id",       sa.String(32),  nullable=False),
        sa.Column("week_start",      sa.String(10),  nullable=False),   # YYYY-MM-DD (Monday)
        sa.Column("completion_rate", sa.Float(),     server_default="0", nullable=False),
        sa.Column("active_goals",    sa.Integer(),   server_default="0", nullable=False),
        sa.Column("completed_goals", sa.Integer(),   server_default="0", nullable=False),
        sa.Column("streak_days",     sa.Integer(),   server_default="0", nullable=False),
        sa.Column("checkins_week",   sa.Integer(),   server_default="0", nullable=False),
        sa.Column("created_at",      sa.DateTime(),  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_snapshots_user_id",    "domain_weekly_snapshots", ["user_id"])
    op.create_index("ix_snapshots_domain_id",  "domain_weekly_snapshots", ["domain_id"])
    op.create_index("ix_snapshots_week_start", "domain_weekly_snapshots", ["week_start"])
    op.create_unique_constraint(
        "uq_snapshot_user_domain_week", "domain_weekly_snapshots",
        ["user_id", "domain_id", "week_start"],
    )


def downgrade() -> None:
    op.drop_table("domain_weekly_snapshots")
    op.drop_table("goal_progress_logs")
    op.drop_table("domain_checkins")
    op.execute("DROP TYPE IF EXISTS checkin_status_enum")
    op.drop_table("domain_goals")
    op.execute("DROP TYPE IF EXISTS goal_status_enum")
