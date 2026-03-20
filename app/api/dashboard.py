# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""User dashboard API with all features."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
import random

from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# In-memory storage (replace with database)
goals_db: dict[str, list[dict]] = {}
recommendations_db: dict[str, list[dict]] = {}
activity_db: dict[str, list[dict]] = {}
notifications_db: dict[str, list[dict]] = {}
mood_db: dict[str, list[dict]] = {}


# ==================== ENUMS ====================

class GoalStatus(str, Enum):
    """Goal status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ActivityType(str, Enum):
    """Activity types."""
    LOGIN = "login"
    GOAL_CREATED = "goal_created"
    GOAL_COMPLETED = "goal_completed"
    RECOMMENDATION_VIEWED = "recommendation_viewed"
    RECOMMENDATION_COMPLETED = "recommendation_completed"
    DECISION_MADE = "decision_made"
    BRIEF_GENERATED = "brief_generated"


# ==================== RESPONSE MODELS ====================

class GoalProgress(BaseModel):
    """Goal progress."""
    id: str
    title: str
    description: str
    status: str
    progress: int  # 0-100
    created_at: str
    updated_at: str


class RecommendationItem(BaseModel):
    """Recommendation item."""
    id: str
    title: str
    description: str
    domain: str
    priority: str  # high, medium, low
    is_completed: bool
    created_at: str


class ActivityItem(BaseModel):
    """Activity item."""
    id: str
    type: str
    title: str
    description: str
    timestamp: str


class OverviewSummary(BaseModel):
    """Overview summary."""
    total_goals: int
    active_goals: int
    completed_goals: int
    total_recommendations: int
    pending_recommendations: int
    streak_days: int
    last_active: str


class DashboardResponse(BaseModel):
    """Full dashboard response."""
    user_id: str
    overview: OverviewSummary
    goals: List[GoalProgress]
    top_recommendations: List[RecommendationItem]
    recent_activity: List[ActivityItem]
    generated_at: str


# ==================== HELPER FUNCTIONS ====================

def generate_demo_goals(user_id: str) -> List[dict]:
    """Generate demo goals for user."""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "Advance career",
            "description": "Get promoted to senior role",
            "status": GoalStatus.ACTIVE.value,
            "progress": 45,
            "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Financial independence",
            "description": "Save 6 months emergency fund",
            "status": GoalStatus.ACTIVE.value,
            "progress": 70,
            "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Health & fitness",
            "description": "Exercise 3x per week",
            "status": GoalStatus.ACTIVE.value,
            "progress": 25,
            "created_at": (datetime.utcnow() - timedelta(days=14)).isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]


def generate_demo_recommendations(user_id: str) -> List[dict]:
    """Generate demo recommendations."""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "Schedule weekly 1:1 with manager",
            "description": "Regular career check-ins help align your goals with team objectives",
            "domain": "career",
            "priority": "high",
            "is_completed": False,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Review monthly expenses",
            "description": "Track spending to identify savings opportunities",
            "domain": "finance",
            "priority": "medium",
            "is_completed": False,
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Add workout to calendar",
            "description": "Schedule exercise like any important meeting",
            "domain": "health",
            "priority": "medium",
            "is_completed": False,
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
        }
    ]


def generate_demo_activity(user_id: str) -> List[dict]:
    """Generate demo activity."""
    return [
        {
            "id": str(uuid.uuid4()),
            "type": ActivityType.LOGIN.value,
            "title": "Logged in",
            "description": "Welcome back!",
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "type": ActivityType.RECOMMENDATION_VIEWED.value,
            "title": "Viewed recommendation",
            "description": "Schedule weekly 1:1 with manager",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "type": ActivityType.BRIEF_GENERATED.value,
            "title": "Generated brief",
            "description": "Weekly executive brief ready",
            "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat()
        }
    ]


# ==================== ROUTES ====================

@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get full dashboard data."""
    
    user_id = current_user.id
    
    # Get or generate goals
    if user_id not in goals_db:
        goals_db[user_id] = generate_demo_goals(user_id)
    goals = goals_db[user_id]
    
    # Get or generate recommendations
    if user_id not in recommendations_db:
        recommendations_db[user_id] = generate_demo_recommendations(user_id)
    recommendations = recommendations_db[user_id]
    
    # Get or generate activity
    if user_id not in activity_db:
        activity_db[user_id] = generate_demo_activity(user_id)
    activity = activity_db[user_id]
    
    # Calculate overview
    active_goals = sum(1 for g in goals if g["status"] == GoalStatus.ACTIVE.value)
    completed_goals = sum(1 for g in goals if g["status"] == GoalStatus.COMPLETED.value)
    pending_recs = sum(1 for r in recommendations if not r["is_completed"])
    
    overview = OverviewSummary(
        total_goals=len(goals),
        active_goals=active_goals,
        completed_goals=completed_goals,
        total_recommendations=len(recommendations),
        pending_recommendations=pending_recs,
        streak_days=random.randint(3, 30),  # Demo data
        last_active=datetime.utcnow().isoformat()
    )
    
    return DashboardResponse(
        user_id=user_id,
        overview=overview,
        goals=[GoalProgress(**g) for g in goals],
        top_recommendations=[RecommendationItem(**r) for r in recommendations[:5]],
        recent_activity=[ActivityItem(**a) for a in activity[:10]],
        generated_at=datetime.utcnow().isoformat()
    )


@router.get("/overview", response_model=OverviewSummary)
async def get_overview(
    current_user: User = Depends(get_current_user)
):
    """Get dashboard overview only."""
    
    user_id = current_user.id
    
    # Get or generate data
    if user_id not in goals_db:
        goals_db[user_id] = generate_demo_goals(user_id)
    if user_id not in recommendations_db:
        recommendations_db[user_id] = generate_demo_recommendations(user_id)
    
    goals = goals_db[user_id]
    recommendations = recommendations_db[user_id]
    
    active_goals = sum(1 for g in goals if g["status"] == GoalStatus.ACTIVE.value)
    completed_goals = sum(1 for g in goals if g["status"] == GoalStatus.COMPLETED.value)
    pending_recs = sum(1 for r in recommendations if not r["is_completed"])
    
    return OverviewSummary(
        total_goals=len(goals),
        active_goals=active_goals,
        completed_goals=completed_goals,
        total_recommendations=len(recommendations),
        pending_recommendations=pending_recs,
        streak_days=random.randint(3, 30),
        last_active=datetime.utcnow().isoformat()
    )


@router.get("/goals", response_model=List[GoalProgress])
async def get_goals(
    current_user: User = Depends(get_current_user)
):
    """Get user goals."""
    
    user_id = current_user.id
    
    if user_id not in goals_db:
        goals_db[user_id] = generate_demo_goals(user_id)
    
    return [GoalProgress(**g) for g in goals_db[user_id]]


@router.post("/goals")
async def create_goal(
    title: str,
    description: str,
    current_user: User = Depends(get_current_user)
):
    """Create a new goal."""
    
    user_id = current_user.id
    
    if user_id not in goals_db:
        goals_db[user_id] = []
    
    goal = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "status": GoalStatus.ACTIVE.value,
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    goals_db[user_id].append(goal)
    
    return {"message": "Goal created", "goal": GoalProgress(**goal)}


@router.patch("/goals/{goal_id}")
async def update_goal(
    goal_id: str,
    progress: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update a goal."""
    
    user_id = current_user.id
    
    if user_id not in goals_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No goals found"
        )
    
    for goal in goals_db[user_id]:
        if goal["id"] == goal_id:
            if progress is not None:
                goal["progress"] = min(100, max(0, progress))
            if status is not None:
                goal["status"] = status
            goal["updated_at"] = datetime.utcnow().isoformat()
            return {"message": "Goal updated", "goal": GoalProgress(**goal)}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Goal not found"
    )


@router.get("/recommendations", response_model=List[RecommendationItem])
async def get_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Get user recommendations."""
    
    user_id = current_user.id
    
    if user_id not in recommendations_db:
        recommendations_db[user_id] = generate_demo_recommendations(user_id)
    
    return [RecommendationItem(**r) for r in recommendations_db[user_id]]


@router.post("/recommendations/{rec_id}/complete")
async def complete_recommendation(
    rec_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark recommendation as completed."""
    
    user_id = current_user.id
    
    if user_id not in recommendations_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found"
        )
    
    for rec in recommendations_db[user_id]:
        if rec["id"] == rec_id:
            rec["is_completed"] = True
            return {"message": "Recommendation completed", "recommendation": RecommendationItem(**rec)}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Recommendation not found"
    )


@router.get("/activity", response_model=List[ActivityItem])
async def get_activity(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get recent activity."""
    
    user_id = current_user.id
    
    if user_id not in activity_db:
        activity_db[user_id] = generate_demo_activity(user_id)
    
    return [ActivityItem(**a) for a in activity_db[user_id][:limit]]


# ==================== NEW FEATURES ====================

# --- Domain Scores ---

class DomainScore(BaseModel):
    """Domain score."""
    domain: str
    name: str
    score: int  # 0-100
    trend: str  # up, down, stable
    icon: str


class DomainScoresResponse(BaseModel):
    """Domain scores response."""
    scores: List[DomainScore]
    overall_score: int


@router.get("/domain-scores", response_model=DomainScoresResponse)
async def get_domain_scores(
    current_user: User = Depends(get_current_user)
):
    """Get domain scores (Career, Finance, Health, etc.)."""
    
    scores = [
        {"domain": "career", "name": "Career", "score": 72, "trend": "up", "icon": "📈"},
        {"domain": "finance", "name": "Finance", "score": 65, "trend": "up", "icon": "💰"},
        {"domain": "health", "name": "Health", "score": 58, "trend": "down", "icon": "💪"},
        {"domain": "relationships", "name": "Relationships", "score": 80, "trend": "stable", "icon": "❤️"},
        {"domain": "personal_growth", "name": "Personal Growth", "score": 75, "trend": "up", "icon": "🌱"},
    ]
    
    overall = sum(s["score"] for s in scores) // len(scores)
    
    return DomainScoresResponse(
        scores=[DomainScore(**s) for s in scores],
        overall_score=overall
    )


# --- Quick Actions ---

class QuickAction(BaseModel):
    """Quick action button."""
    id: str
    label: str
    icon: str
    action: str  # endpoint to call
    requires_auth: bool = True


class QuickActionsResponse(BaseModel):
    """Quick actions response."""
    actions: List[QuickAction]


@router.get("/quick-actions", response_model=QuickActionsResponse)
async def get_quick_actions(
    current_user: User = Depends(get_current_user)
):
    """Get quick action buttons."""
    
    actions = [
        {"id": "new_goal", "label": "New Goal", "icon": "🎯", "action": "/dashboard/goals"},
        {"id": "generate_brief", "label": "Generate Brief", "icon": "📋", "action": "/briefs/generate"},
        {"id": "chat", "label": "AI Chat", "icon": "💬", "action": "/chat"},
        {"id": "view_recommendations", "label": "Recommendations", "icon": "💡", "action": "/dashboard/recommendations"},
        {"id": "check_mood", "label": "Mood Check-in", "icon": "😊", "action": "/dashboard/mood"},
        {"id": "calendar", "label": "Calendar", "icon": "📅", "action": "/dashboard/calendar"},
    ]
    
    return QuickActionsResponse(
        actions=[QuickAction(**a) for a in actions]
    )


# --- Calendar Events ---

class CalendarEvent(BaseModel):
    """Calendar event."""
    id: str
    title: str
    description: str
    date: str
    time: Optional[str] = None
    type: str  # deadline, meeting, reminder
    related_goal_id: Optional[str] = None


class CalendarResponse(BaseModel):
    """Calendar response."""
    events: List[CalendarEvent]
    upcoming_count: int


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar_events(
    current_user: User = Depends(get_current_user),
    days: int = 7
):
    """Get upcoming calendar events."""
    
    user_id = current_user.id
    
    # Generate demo events
    events = [
        {
            "id": str(uuid.uuid4()),
            "title": "Weekly 1:1 with Manager",
            "description": "Career progress review",
            "date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "10:00 AM",
            "type": "meeting",
            "related_goal_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Review Emergency Fund",
            "description": "Monthly finance check",
            "date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "time": "2:00 PM",
            "type": "reminder",
            "related_goal_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Quarterly Review",
            "description": "End of Q1 review",
            "date": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "time": "9:00 AM",
            "type": "deadline",
            "related_goal_id": None
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Gym Session",
            "description": "Scheduled workout",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "time": "6:00 PM",
            "type": "meeting",
            "related_goal_id": None
        }
    ]
    
    return CalendarResponse(
        events=[CalendarEvent(**e) for e in events],
        upcoming_count=len(events)
    )


# --- Notifications ---

class NotificationItem(BaseModel):
    """Notification item."""
    id: str
    title: str
    message: str
    type: str  # info, warning, success, error
    is_read: bool
    created_at: str


class NotificationsResponse(BaseModel):
    """Notifications response."""
    notifications: List[NotificationItem]
    unread_count: int


@router.get("/notifications", response_model=NotificationsResponse)
async def get_notifications(
    current_user: User = Depends(get_current_user)
):
    """Get user notifications."""
    
    user_id = current_user.id
    
    # Generate demo notifications
    notifications = [
        {
            "id": str(uuid.uuid4()),
            "title": "Goal milestone! 🎉",
            "message": "You've reached 50% on 'Advance career' goal",
            "type": "success",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "New recommendation",
            "message": "Check out today's top recommendation",
            "type": "info",
            "is_read": False,
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Weekly brief ready",
            "message": "Your executive brief is ready to view",
            "type": "info",
            "is_read": True,
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Health reminder",
            "message": "You haven't logged a workout in 3 days",
            "type": "warning",
            "is_read": False,
            "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
        }
    ]
    
    unread = sum(1 for n in notifications if not n["is_read"])
    
    return NotificationsResponse(
        notifications=[NotificationItem(**n) for n in notifications],
        unread_count=unread
    )


@router.post("/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read."""
    
    return {"message": "Notification marked as read", "notif_id": notif_id}


# --- Mood Tracking ---

class MoodEntry(BaseModel):
    """Mood entry."""
    id: str
    mood: str  # great, good, okay, bad, terrible
    note: Optional[str] = None
    created_at: str


class MoodResponse(BaseModel):
    """Mood response."""
    today_mood: Optional[MoodEntry] = None
    weekly_moods: List[MoodEntry]
    average_mood: float


MOOD_SCORES = {"terrible": 1, "bad": 2, "okay": 3, "good": 4, "great": 5}


@router.get("/mood", response_model=MoodResponse)
async def get_mood_data(
    current_user: User = Depends(get_current_user)
):
    """Get mood tracking data."""
    
    user_id = current_user.id
    
    # Generate demo mood entries
    moods = [
        {"id": str(uuid.uuid4()), "mood": "good", "note": "Great day!", "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat()}
        for i in range(7)
    ]
    
    # Add some variety
    moods[0]["mood"] = "great"
    moods[1]["mood"] = "good"
    moods[2]["mood"] = "okay"
    moods[3]["mood"] = "good"
    moods[4]["mood"] = "great"
    moods[5]["mood"] = "okay"
    moods[6]["mood"] = "good"
    
    scores = [MOOD_SCORES.get(m["mood"], 3) for m in moods]
    average = sum(scores) / len(scores) if scores else 3.0
    
    return MoodResponse(
        today_mood=MoodEntry(**moods[0]) if moods else None,
        weekly_moods=[MoodEntry(**m) for m in moods],
        average_mood=round(average, 1)
    )


@router.post("/mood")
async def log_mood(
    mood: str,
    note: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Log today's mood."""
    
    valid_moods = ["terrible", "bad", "okay", "good", "great"]
    if mood not in valid_moods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mood. Valid: {valid_moods}"
        )
    
    entry = {
        "id": str(uuid.uuid4()),
        "mood": mood,
        "note": note,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {"message": "Mood logged", "entry": MoodEntry(**entry)}


# --- Charts Data ---

class ChartDataPoint(BaseModel):
    """Chart data point."""
    label: str
    value: float


class ChartResponse(BaseModel):
    """Chart response."""
    goal_progress: List[ChartDataPoint]
    weekly_activity: List[ChartDataPoint]
    mood_trend: List[ChartDataPoint]


@router.get("/charts", response_model=ChartResponse)
async def get_chart_data(
    current_user: User = Depends(get_current_user)
):
    """Get chart data for visualizations."""
    
    # Goal progress chart
    goal_progress = [
        {"label": "Career", "value": 45},
        {"label": "Finance", "value": 70},
        {"label": "Health", "value": 25},
        {"label": "Relationships", "value": 80},
        {"label": "Growth", "value": 60},
    ]
    
    # Weekly activity chart
    weekly_activity = [
        {"label": "Mon", "value": 85},
        {"label": "Tue", "value": 72},
        {"label": "Wed", "value": 90},
        {"label": "Thu", "value": 65},
        {"label": "Fri", "value": 78},
        {"label": "Sat", "value": 45},
        {"label": "Sun", "value": 30},
    ]
    
    # Mood trend chart
    mood_trend = [
        {"label": "Mon", "value": 4},
        {"label": "Tue", "value": 3.5},
        {"label": "Wed", "value": 4.5},
        {"label": "Thu", "value": 3},
        {"label": "Fri", "value": 4},
        {"label": "Sat", "value": 3.5},
        {"label": "Sun", "value": 4},
    ]
    
    return ChartResponse(
        goal_progress=[ChartDataPoint(**p) for p in goal_progress],
        weekly_activity=[ChartDataPoint(**a) for a in weekly_activity],
        mood_trend=[ChartDataPoint(**m) for m in mood_trend]
    )


# --- Updates/News ---

class UpdateItem(BaseModel):
    """Platform update."""
    id: str
    title: str
    description: str
    date: str
    type: str  # feature, fix, announcement


@router.get("/updates", response_model=List[UpdateItem])
async def get_platform_updates(
    current_user: User = Depends(get_current_user)
):
    """Get platform updates/changelog."""
    
    updates = [
        {
            "id": str(uuid.uuid4()),
            "title": "🎉 New Dashboard Features",
            "description": "We've added charts, mood tracking, and calendar views!",
            "date": (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "type": "feature"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "⚡ Performance Improvements",
            "description": "Faster load times and smoother animations",
            "date": (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "type": "fix"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "📱 Mobile App Coming Soon",
            "description": "We're working on a mobile app - stay tuned!",
            "date": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "type": "announcement"
        }
    ]
    
    return [UpdateItem(**u) for u in updates]


# --- Full Enhanced Dashboard ---

class EnhancedDashboardResponse(BaseModel):
    """Full enhanced dashboard with all features."""
    user_id: str
    overview: OverviewSummary
    goals: List[GoalProgress]
    top_recommendations: List[RecommendationItem]
    recent_activity: List[ActivityItem]
    domain_scores: List[DomainScore]
    quick_actions: List[QuickAction]
    upcoming_events: List[CalendarEvent]
    notifications: List[NotificationItem]
    charts: ChartResponse
    generated_at: str


@router.get("/enhanced", response_model=EnhancedDashboardResponse)
async def get_enhanced_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get full enhanced dashboard with all features."""
    
    user_id = current_user.id
    
    # Get or generate all data
    if user_id not in goals_db:
        goals_db[user_id] = generate_demo_goals(user_id)
    if user_id not in recommendations_db:
        recommendations_db[user_id] = generate_demo_recommendations(user_id)
    if user_id not in activity_db:
        activity_db[user_id] = generate_demo_activity(user_id)
    
    goals = goals_db[user_id]
    recommendations = recommendations_db[user_id]
    activity = activity_db[user_id]
    
    # Overview
    active_goals = sum(1 for g in goals if g["status"] == GoalStatus.ACTIVE.value)
    completed_goals = sum(1 for g in goals if g["status"] == GoalStatus.COMPLETED.value)
    pending_recs = sum(1 for r in recommendations if not r["is_completed"])
    
    overview = OverviewSummary(
        total_goals=len(goals),
        active_goals=active_goals,
        completed_goals=completed_goals,
        total_recommendations=len(recommendations),
        pending_recommendations=pending_recs,
        streak_days=random.randint(3, 30),
        last_active=datetime.utcnow().isoformat()
    )
    
    # Domain scores
    domain_scores_data = [
        {"domain": "career", "name": "Career", "score": 72, "trend": "up", "icon": "📈"},
        {"domain": "finance", "name": "Finance", "score": 65, "trend": "up", "icon": "💰"},
        {"domain": "health", "name": "Health", "score": 58, "trend": "down", "icon": "💪"},
        {"domain": "relationships", "name": "Relationships", "score": 80, "trend": "stable", "icon": "❤️"},
        {"domain": "personal_growth", "name": "Personal Growth", "score": 75, "trend": "up", "icon": "🌱"},
    ]
    
    # Quick actions
    actions = [
        {"id": "new_goal", "label": "New Goal", "icon": "🎯", "action": "/dashboard/goals"},
        {"id": "generate_brief", "label": "Generate Brief", "icon": "📋", "action": "/briefs/generate"},
        {"id": "chat", "label": "AI Chat", "icon": "💬", "action": "/chat"},
    ]
    
    # Calendar events
    events = [
        {
            "id": str(uuid.uuid4()),
            "title": "Weekly 1:1",
            "description": "Career review",
            "date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "10:00 AM",
            "type": "meeting",
            "related_goal_id": None
        }
    ]
    
    # Notifications
    notifs = [
        {
            "id": str(uuid.uuid4()),
            "title": "Goal milestone! 🎉",
            "message": "50% on career goal",
            "type": "success",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    # Charts
    charts = ChartResponse(
        goal_progress=[ChartDataPoint(**p) for p in [
            {"label": "Career", "value": 45},
            {"label": "Finance", "value": 70},
            {"label": "Health", "value": 25},
        ]],
        weekly_activity=[ChartDataPoint(**a) for a in [
            {"label": "Mon", "value": 85},
            {"label": "Tue", "value": 72},
        ]],
        mood_trend=[ChartDataPoint(**m) for m in [
            {"label": "Mon", "value": 4},
            {"label": "Tue", "value": 3.5},
        ]]
    )
    
    return EnhancedDashboardResponse(
        user_id=user_id,
        overview=overview,
        goals=[GoalProgress(**g) for g in goals],
        top_recommendations=[RecommendationItem(**r) for r in recommendations[:5]],
        recent_activity=[ActivityItem(**a) for a in activity[:10]],
        domain_scores=[DomainScore(**d) for d in domain_scores_data],
        quick_actions=[QuickAction(**a) for a in actions],
        upcoming_events=[CalendarEvent(**e) for e in events],
        notifications=[NotificationItem(**n) for n in notifs],
        charts=charts,
        generated_at=datetime.utcnow().isoformat()
    )
