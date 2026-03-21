# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""SQLAlchemy models for Domain Goals, Check-ins, Progress Log, and Weekly Snapshots.

HOW TO ADD:
  1. cp db_models.py app/models/domain_models.py
  2. In app/models/__init__.py add:
       from app.models.domain_models import (
           DomainGoal, DomainCheckIn, GoalProgressLog, DomainWeeklySnapshot
       )
  3. Run migration (see alembic_migration.py)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String, Integer, Float, DateTime, ForeignKey, Text,
    Enum as SAEnum, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base   # ← adjust if needed


def _uuid() -> str:
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# DomainGoal
# ─────────────────────────────────────────────────────────────────────────────

class DomainGoal(Base):
    __tablename__ = "domain_goals"

    id:          Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id:     Mapped[str]           = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id:   Mapped[str]           = mapped_column(String(32), nullable=False, index=True)
    title:       Mapped[str]           = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category:    Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    progress:    Mapped[int]           = mapped_column(Integer, default=0)
    status:      Mapped[str]           = mapped_column(
        SAEnum("active", "completed", "paused", name="goal_status_enum"),
        default="active", nullable=False,
    )
    target_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at:  Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at:  Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "progress": self.progress,
            "status": self.status,
            "target_date": self.target_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
# DomainCheckIn
# ─────────────────────────────────────────────────────────────────────────────

class DomainCheckIn(Base):
    __tablename__ = "domain_checkins"
    __table_args__ = (
        UniqueConstraint("user_id", "domain_id", "date", name="uq_checkin_user_domain_date"),
    )

    id:        Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id:   Mapped[str]           = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id: Mapped[str]           = mapped_column(String(32), nullable=False, index=True)
    date:      Mapped[str]           = mapped_column(String(10), nullable=False)
    status:    Mapped[str]           = mapped_column(
        SAEnum("completed", "partial", "missed", name="checkin_status_enum"),
        default="completed", nullable=False,
    )
    notes:      Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "date": self.date,
            "status": self.status,
            "notes": self.notes,
            "metrics": None,
        }


# ─────────────────────────────────────────────────────────────────────────────
# GoalProgressLog
# ─────────────────────────────────────────────────────────────────────────────

class GoalProgressLog(Base):
    """Append-only log of every progress update. Feeds goal sparklines."""
    __tablename__ = "goal_progress_logs"

    id:        Mapped[str]      = mapped_column(String(36), primary_key=True, default=_uuid)
    goal_id:   Mapped[str]      = mapped_column(String(36), ForeignKey("domain_goals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id:   Mapped[str]      = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    progress:  Mapped[int]      = mapped_column(Integer, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "progress": self.progress,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
# DomainWeeklySnapshot  ← NEW
# ─────────────────────────────────────────────────────────────────────────────

class DomainWeeklySnapshot(Base):
    """One row per user per domain per ISO week.
    Written by the weekly cron job (or on-demand via POST /domains/snapshot).
    Feeds the radar chart on the Domains page.
    """
    __tablename__ = "domain_weekly_snapshots"
    __table_args__ = (
        # Enforce one row per user + domain + week
        UniqueConstraint("user_id", "domain_id", "week_start", name="uq_snapshot_user_domain_week"),
    )

    id:              Mapped[str]   = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id:         Mapped[str]   = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id:       Mapped[str]   = mapped_column(String(32), nullable=False, index=True)

    # ISO week start date (Monday), e.g. "2026-03-16"
    week_start:      Mapped[str]   = mapped_column(String(10), nullable=False, index=True)

    # Scores captured at snapshot time
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)   # 0-100
    active_goals:    Mapped[int]   = mapped_column(Integer, default=0, nullable=False)
    completed_goals: Mapped[int]   = mapped_column(Integer, default=0, nullable=False)
    streak_days:     Mapped[int]   = mapped_column(Integer, default=0, nullable=False)
    checkins_week:   Mapped[int]   = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime]   = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "week_start": self.week_start,
            "completion_rate": self.completion_rate,
            "active_goals": self.active_goals,
            "completed_goals": self.completed_goals,
            "streak_days": self.streak_days,
            "checkins_week": self.checkins_week,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
