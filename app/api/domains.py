# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Life Domains API - Track different areas of life."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
import random

from app.models.database import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/domains", tags=["Life Domains"])


# ==================== DOMAIN DEFINITIONS ====================

DOMAINS = {
    "health": {
        "id": "health",
        "name": "Health",
        "icon": "🏃",
        "color": "green",
        "description": "Physical wellbeing, fitness, and nutrition",
        "categories": ["Fitness", "Sleep", "Nutrition", "Medical", "Mental Health"]
    },
    "career": {
        "id": "career", 
        "name": "Career",
        "icon": "💼",
        "color": "blue",
        "description": "Professional growth and skill development",
        "categories": ["Skills", "Work", "Business", "Learning", "Networking"]
    },
    "mindset": {
        "id": "mindset",
        "name": "Mindset", 
        "icon": "🧠",
        "color": "purple",
        "description": "Mental wellness and personal growth",
        "categories": ["Meditation", "Gratitude", "Journaling", "Reading", "Self-care"]
    },
    "habits": {
        "id": "habits",
        "name": "Habits",
        "icon": "🔄",
        "color": "orange",
        "description": "Daily routines and habit building",
        "categories": ["Morning Routine", "Evening Routine", "Productivity", "Learning", "Wellness"]
    },
    "relationships": {
        "id": "relationships",
        "name": "Relationships",
        "icon": "👥",
        "color": "pink",
        "description": "Connections with friends, family, and partner",
        "categories": ["Family", "Friends", "Partner", "Social", "Community"]
    },
    "finance": {
        "id": "finance",
        "name": "Finance",
        "icon": "💰",
        "color": "yellow",
        "description": "Money management and financial goals",
        "categories": ["Budgeting", "Saving", "Investing", "Income", "Debt"]
    }
}


# ==================== MODELS ====================

class Domain(BaseModel):
    """Life domain."""
    id: str
    name: str
    icon: str
    color: str
    description: str
    categories: List[str]


class DomainGoal(BaseModel):
    """Goal within a domain."""
    id: str
    domain_id: str
    title: str
    description: Optional[str]
    category: str
    progress: int = 0
    status: str = "active"
    target_date: Optional[str]
    created_at: str


class DailyCheckIn(BaseModel):
    """Daily check-in for a domain."""
    id: str
    domain_id: str
    date: str
    status: str  # completed, partial, missed
    notes: Optional[str]
    metrics: Optional[dict]


class DomainProgress(BaseModel):
    """Progress summary for a domain."""
    domain_id: str
    total_goals: int
    completed_goals: int
    active_goals: int
    current_streak: int
    weekly_checkins: int
    completion_rate: float


class DomainStats(BaseModel):
    """Statistics for a domain."""
    domain_id: str
    goals_this_month: int
    completed_this_month: int
    checkins_this_week: int
    streak_days: int
    avg_progress: float


# ==================== ENDPOINTS ====================

@router.get("", response_model=List[Domain])
async def get_domains():
    """Get all life domains."""
    return list(DOMAINS.values())


@router.get("/{domain_id}", response_model=Domain)
async def get_domain(domain_id: str):
    """Get a specific domain."""
    if domain_id not in DOMAINS:
        return {"error": "Domain not found"}
    return DOMAINS[domain_id]


@router.get("/{domain_id}/goals", response_model=List[DomainGoal])
async def get_domain_goals(
    domain_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get goals for a specific domain."""
    
    # Generate demo goals for each domain
    demo_goals = {
        "health": [
            {"id": "h1", "domain_id": "health", "title": "Exercise 3x per week", "description": "Go to the gym or do home workout", "category": "Fitness", "progress": 75, "status": "active"},
            {"id": "h2", "domain_id": "health", "title": "Sleep 8 hours daily", "description": "Maintain consistent sleep schedule", "category": "Sleep", "progress": 60, "status": "active"},
            {"id": "h3", "domain_id": "health", "title": "Drink 8 glasses of water", "description": "Stay hydrated throughout the day", "category": "Nutrition", "progress": 100, "status": "completed"},
        ],
        "career": [
            {"id": "c1", "domain_id": "career", "title": "Learn Python", "description": "Complete Python course", "category": "Learning", "progress": 45, "status": "active"},
            {"id": "c2", "domain_id": "career", "title": "Network weekly", "description": "Connect with 2 professionals", "category": "Networking", "progress": 30, "status": "active"},
        ],
        "mindset": [
            {"id": "m1", "domain_id": "mindset", "title": "Meditate daily", "description": "10 minutes morning meditation", "category": "Meditation", "progress": 80, "status": "active"},
            {"id": "m2", "domain_id": "mindset", "title": "Gratitude journal", "description": "Write 3 things grateful for", "category": "Gratitude", "progress": 55, "status": "active"},
        ],
        "habits": [
            {"id": "ha1", "domain_id": "habits", "title": "Morning routine", "description": "Wake up at 6am, exercise, shower", "category": "Morning Routine", "progress": 65, "status": "active"},
            {"id": "ha2", "domain_id": "habits", "title": "No social media before noon", "description": "Stay focused in the morning", "category": "Productivity", "progress": 40, "status": "active"},
        ],
        "relationships": [
            {"id": "r1", "domain_id": "relationships", "title": "Call parents weekly", "description": "Check in with parents every Sunday", "category": "Family", "progress": 85, "status": "active"},
            {"id": "r2", "domain_id": "relationships", "title": "Date night", "description": "Weekly date with partner", "category": "Partner", "progress": 100, "status": "completed"},
        ],
        "finance": [
            {"id": "f1", "domain_id": "finance", "title": "Save $1000/mo", "description": "Build emergency fund", "category": "Saving", "progress": 70, "status": "active"},
            {"id": "f2", "domain_id": "finance", "title": "Track expenses", "description": "Log all spending daily", "category": "Budgeting", "progress": 90, "status": "active"},
        ],
    }
    
    return demo_goals.get(domain_id, [])


@router.get("/{domain_id}/progress", response_model=DomainProgress)
async def get_domain_progress(
    domain_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get progress summary for a domain."""
    
    # Generate demo progress
    progress_data = {
        "health": {"total": 8, "completed": 3, "active": 5, "streak": 12, "weekly_checkins": 5, "rate": 65},
        "career": {"total": 5, "completed": 1, "active": 4, "streak": 8, "weekly_checkins": 4, "rate": 45},
        "mindset": {"total": 6, "completed": 2, "active": 4, "streak": 15, "weekly_checkins": 6, "rate": 72},
        "habits": {"total": 10, "completed": 4, "active": 6, "streak": 23, "weekly_checkins": 7, "rate": 58},
        "relationships": {"total": 4, "completed": 2, "active": 2, "streak": 6, "weekly_checkins": 3, "rate": 80},
        "finance": {"total": 6, "completed": 2, "active": 4, "streak": 30, "weekly_checkins": 7, "rate": 85},
    }
    
    data = progress_data.get(domain_id, {"total": 0, "completed": 0, "active": 0, "streak": 0, "weekly_checkins": 0, "rate": 0})
    
    return DomainProgress(
        domain_id=domain_id,
        total_goals=data["total"],
        completed_goals=data["completed"],
        active_goals=data["active"],
        current_streak=data["streak"],
        weekly_checkins=data["weekly_checkins"],
        completion_rate=data["rate"]
    )


@router.get("/{domain_id}/stats", response_model=DomainStats)
async def get_domain_stats(
    domain_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed stats for a domain."""
    
    # Generate demo stats
    stats = {
        "health": {"goals_month": 3, "completed_month": 2, "checkins_week": 5, "streak": 12, "avg_progress": 78},
        "career": {"goals_month": 2, "completed_month": 0, "checkins_week": 3, "streak": 8, "avg_progress": 42},
        "mindset": {"goals_month": 4, "completed_month": 1, "checkins_week": 6, "streak": 15, "avg_progress": 65},
        "habits": {"goals_month": 5, "completed_month": 3, "checkins_week": 7, "streak": 23, "avg_progress": 55},
        "relationships": {"goals_month": 2, "completed_month": 1, "checkins_week": 2, "streak": 6, "avg_progress": 72},
        "finance": {"goals_month": 3, "completed_month": 1, "checkins_week": 7, "streak": 30, "avg_progress": 82},
    }
    
    data = stats.get(domain_id, {"goals_month": 0, "completed_month": 0, "checkins_week": 0, "streak": 0, "avg_progress": 0})
    
    return DomainStats(
        domain_id=domain_id,
        goals_this_month=data["goals_month"],
        completed_this_month=data["completed_month"],
        checkins_this_week=data["checkins_week"],
        streak_days=data["streak"],
        avg_progress=data["avg_progress"]
    )


@router.get("/{domain_id}/checkins", response_model=List[DailyCheckIn])
async def get_domain_checkins(
    domain_id: str,
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user)
):
    """Get daily check-ins for a domain."""
    
    checkins = []
    statuses = ["completed", "completed", "completed", "partial", "missed"]
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i - 1)
        checkins.append({
            "id": f"checkin_{domain_id}_{i}",
            "domain_id": domain_id,
            "date": date.strftime("%Y-%m-%d"),
            "status": statuses[i % len(statuses)],
            "notes": None,
            "metrics": None
        })
    
    return checkins


@router.post("/{domain_id}/checkin")
async def create_checkin(
    domain_id: str,
    status: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Create a daily check-in for a domain."""
    
    return {
        "id": f"checkin_{domain_id}_{datetime.utcnow().timestamp()}",
        "domain_id": domain_id,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "status": status,
        "notes": notes,
        "created": True
    }


@router.get("/progress/all", response_model=dict)
async def get_all_domains_progress(
    current_user: User = Depends(get_current_user)
):
    """Get progress summary for all domains."""
    
    progress_data = {}
    for domain_id in DOMAINS.keys():
        progress_data[domain_id] = {
            "domain": DOMAINS[domain_id],
            "total_goals": random.randint(3, 10),
            "completed_goals": random.randint(1, 5),
            "active_goals": random.randint(2, 6),
            "current_streak": random.randint(5, 30),
            "weekly_checkins": random.randint(3, 7),
            "completion_rate": random.randint(40, 90)
        }
    
    return progress_data
