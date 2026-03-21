# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Analytics API for tracking and reporting."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
import random

from app.models.database import User
from app.api.auth import get_current_user, require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# In-memory storage (replace with database in production)
events_db = []
daily_metrics_db = {}


# ==================== REQUEST/RESPONSE MODELS ====================

class EventTrackRequest(BaseModel):
    """Track an event."""
    event_type: str
    event_name: Optional[str] = None
    event_data: Optional[dict] = None


class EventResponse(BaseModel):
    """Event response."""
    status: str
    event_id: str


class UserStatsResponse(BaseModel):
    """User statistics response."""
    total_goals: int
    completed_goals: int
    active_goals: int
    total_tasks: int
    completed_tasks: int
    current_streak: int
    longest_streak: int
    total_sessions: int
    avg_session_duration: float


class DashboardStatsResponse(BaseModel):
    """Dashboard stats response."""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    total_goals: int
    completed_goals: int
    total_tasks: int
    completed_tasks: int


class RevenueMetricsResponse(BaseModel):
    """Revenue metrics response."""
    mrr: float
    arr: float
    total_revenue: float
    new_subscriptions: int
    canceled_subscriptions: int
    churn_rate: float
    arpu: float  # Average revenue per user


class UsageMetricsResponse(BaseModel):
    """Usage metrics response."""
    daily_active_users: list
    weekly_active_users: list
    monthly_active_users: int
    avg_session_duration: float
    page_views_today: int
    top_features: list


class RetentionResponse(BaseModel):
    """Retention metrics response."""
    daily_retention: list
    weekly_retention: list
    monthly_retention: float


# ==================== EVENT TRACKING ====================

@router.post("/track", response_model=EventResponse)
async def track_event(
    request: EventTrackRequest,
    current_user: User = Depends(get_current_user)
):
    """Track a user event."""
    
    import uuid
    
    event = {
        "id": str(uuid.uuid4()),
        "event_type": request.event_type,
        "event_name": request.event_name,
        "event_data": request.event_data,
        "user_id": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    events_db.append(event)
    
    return EventResponse(
        status="tracked",
        event_id=event["id"]
    )


# ==================== USER ANALYTICS ====================

@router.get("/users/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user)
):
    """Get current user's analytics stats."""
    
    # Generate demo stats
    return UserStatsResponse(
        total_goals=12,
        completed_goals=8,
        active_goals=4,
        total_tasks=47,
        completed_tasks=39,
        current_streak=23,
        longest_streak=45,
        total_sessions=156,
        avg_session_duration=1245.5  # ~21 minutes
    )


@router.get("/users/activity", response_model=dict)
async def get_user_activity(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """Get user's activity over time."""
    
    # Generate demo data
    data = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i - 1)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "page_views": random.randint(5, 50),
            "api_calls": random.randint(20, 200),
            "goals_viewed": random.randint(1, 10),
            "tasks_completed": random.randint(0, 8),
            "time_spent": random.randint(300, 3600)  # seconds
        })
    
    return {"activity": data}


# ==================== DASHBOARD ANALYTICS ====================

@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(require_admin)
):
    """Get platform-wide dashboard statistics."""
    
    # Generate demo stats
    return DashboardStatsResponse(
        total_users=1247,
        active_users=892,
        new_users_today=23,
        new_users_this_week=145,
        new_users_this_month=623,
        total_goals=3456,
        completed_goals=2156,
        total_tasks=12453,
        completed_tasks=9876
    )


@router.get("/revenue", response_model=RevenueMetricsResponse)
async def get_revenue_metrics(
    current_user: User = Depends(require_admin)
):
    """Get revenue analytics."""
    
    return RevenueMetricsResponse(
        mrr=45230.00,
        arr=542760.00,
        total_revenue=324567.00,
        new_subscriptions=45,
        canceled_subscriptions=8,
        churn_rate=2.3,
        arpu=36.25
    )


@router.get("/usage", response_model=UsageMetricsResponse)
async def get_usage_metrics(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(require_admin)
):
    """Get platform usage analytics."""
    
    # Generate daily active users
    dau = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        dau.append({
            "date": date,
            "count": random.randint(400, 900)
        })
    
    return UsageMetricsResponse(
        daily_active_users=dau,
        weekly_active_users=[random.randint(600, 1000) for _ in range(4)],
        monthly_active_users=892,
        avg_session_duration=1245.5,
        page_views_today=4523,
        top_features=[
            {"name": "Goals", "usage": 82},
            {"name": "Tasks", "usage": 67},
            {"name": "Dashboard", "usage": 95},
            {"name": "Finance", "usage": 45},
            {"name": "Profile", "usage": 34}
        ]
    )


@router.get("/retention", response_model=RetentionResponse)
async def get_retention_metrics(
    current_user: User = Depends(require_admin)
):
    """Get user retention analytics."""
    
    return RetentionResponse(
        daily_retention=[
            {"day": i, "retention": max(100 - i * 2.5, 20)} 
            for i in range(1, 8)
        ],
        weekly_retention=[
            {"week": i, "retention": max(70 - i * 5, 30)} 
            for i in range(1, 5)
        ],
        monthly_retention=42.5
    )


@router.get("/events", response_model=dict)
async def get_events(
    event_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin)
):
    """Get recent events."""
    
    # Return demo events
    events = [
        {"type": "page_view", "name": "dashboard", "count": 4523},
        {"type": "page_view", "name": "goals", "count": 3210},
        {"type": "button_click", "name": "create_goal", "count": 892},
        {"type": "button_click", "name": "complete_task", "count": 2341},
        {"type": "feature_used", "name": "finance", "count": 567},
        {"type": "feature_used", "name": "ai_chat", "count": 1234},
    ]
    
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    
    return {"events": events[:limit]}


@router.get("/funnels", response_model=dict)
async def get_funnel_analysis(
    current_user: User = Depends(require_admin)
):
    """Get user funnel analysis."""
    
    return {
        "onboarding_funnel": [
            {"step": "Sign Up", "count": 1000, "percentage": 100},
            {"step": "Email Verified", "count": 780, "percentage": 78},
            {"step": "Onboarding Started", "count": 650, "percentage": 65},
            {"step": "Onboarding Completed", "count": 420, "percentage": 42},
            {"step": "First Goal Created", "count": 380, "percentage": 38},
            {"step": "First Task Completed", "count": 290, "percentage": 29}
        ],
        "subscription_funnel": [
            {"step": "Free User", "count": 1000, "percentage": 100},
            {"step": "Viewed Pricing", "count": 450, "percentage": 45},
            {"step": "Started Checkout", "count": 120, "percentage": 12},
            {"step": "Completed Payment", "count": 85, "percentage": 8.5}
        ]
    }


@router.get("/cohorts", response_model=dict)
async def get_cohort_analysis(
    current_user: User = Depends(require_admin)
):
    """Get cohort analysis."""
    
    cohorts = []
    for i in range(6):
        month = (datetime.utcnow() - timedelta(days=30 * i)).strftime("%Y-%m")
        cohorts.append({
            "cohort": month,
            "size": random.randint(80, 150),
            "retention": [random.randint(60, 100 - i * 8) for _ in range(4)]
        })
    
    return {"cohorts": cohorts}


# ==================== EXPORT ====================

@router.get("/export", response_model=dict)
async def export_analytics(
    format: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin)
):
    """Export analytics data."""
    
    return {
        "format": format,
        "period_days": days,
        "status": "ready",
        "download_url": f"/analytics/download?format={format}&days={days}",
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }
