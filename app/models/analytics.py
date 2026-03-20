# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Analytics models for tracking events and metrics."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Text, Index
from app.database import Base


class AnalyticsEvent(Base):
    """Track user events for analytics."""
    __tablename__ = "analytics_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event data
    event_type = Column(String(100), nullable=False, index=True)  # page_view, button_click, etc.
    event_name = Column(String(200))
    event_data = Column(Text)  # JSON data
    
    # User data
    user_id = Column(String(36), index=True)
    session_id = Column(String(100), index=True)
    
    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    referrer = Column(String(500))
    url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UserActivity(Base):
    """Daily user activity summary."""
    __tablename__ = "user_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    
    # Activity counts
    page_views = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    goals_viewed = Column(Integer, default=0)
    goals_created = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    finance_views = Column(Integer, default=0)
    
    # Session info
    session_count = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, default=0)
    
    # Date
    date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyMetrics(Base):
    """Daily platform-wide metrics."""
    __tablename__ = "daily_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # User metrics
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    
    # Engagement metrics
    total_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0)  # seconds
    page_views = Column(Integer, default=0)
    
    # Feature usage
    goals_created = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    finance_connected = Column(Integer, default=0)
    
    # Revenue metrics
    new_subscriptions = Column(Integer, default=0)
    canceled_subscriptions = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class FeatureUsage(Base):
    """Track feature usage statistics."""
    __tablename__ = "feature_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_name = Column(String(100), nullable=False, index=True)
    
    # Usage stats
    total_usage_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    
    # Time period
    period = Column(String(20))  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class RetentionCohort(Base):
    """Track user retention by cohort."""
    __tablename__ = "retention_cohorts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Cohort info
    cohort_date = Column(DateTime, nullable=False, index=True)
    cohort_size = Column(Integer, default=0)
    
    # Retention by day
    d1_retention = Column(Float)  # Day 1
    d7_retention = Column(Float)  # Day 7
    d14_retention = Column(Float) # Day 14
    d30_retention = Column(Float) # Day 30
    d60_retention = Column(Float) # Day 60
    d90_retention = Column(Float) # Day 90
    
    created_at = Column(DateTime, default=datetime.utcnow)


import uuid
