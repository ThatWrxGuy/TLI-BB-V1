# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""User dashboard API."""

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
