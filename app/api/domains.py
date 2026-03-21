# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Life Domains API - Track different areas of life.
   PATCHED: Added goal persistence (create, update progress, delete),
            real DB-backed check-ins, and /progress/all endpoint.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
import uuid
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

# ==================== IN-MEMORY STORE (swap for DB later) ====================
# Keyed by user_id -> domain_id -> list of goals / check-ins
# For production: replace _goal_store / _checkin_store with SQLAlchemy queries.

_goal_store: dict[str, dict[str, list]] = {}
_checkin_store: dict[str, dict[str, list]] = {}
_snapshot_store: dict[str, list] = {}  # user_id -> list of snapshots

DEMO_GOALS = {
    "health": [
        {"id": "h1", "domain_id": "health", "title": "Exercise 3x per week", "description": "Go to the gym or do home workout", "category": "Fitness", "progress": 75, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "h2", "domain_id": "health", "title": "Sleep 8 hours daily", "description": "Maintain consistent sleep schedule", "category": "Sleep", "progress": 60, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "h3", "domain_id": "health", "title": "Drink 8 glasses of water", "description": "Stay hydrated throughout the day", "category": "Nutrition", "progress": 100, "status": "completed", "target_date": None, "created_at": "2026-01-01T00:00:00"},
    ],
    "career": [
        {"id": "c1", "domain_id": "career", "title": "Learn Python", "description": "Complete Python course", "category": "Learning", "progress": 45, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "c2", "domain_id": "career", "title": "Network weekly", "description": "Connect with 2 professionals", "category": "Networking", "progress": 30, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
    ],
    "mindset": [
        {"id": "m1", "domain_id": "mindset", "title": "Meditate daily", "description": "10 minutes morning meditation", "category": "Meditation", "progress": 80, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "m2", "domain_id": "mindset", "title": "Gratitude journal", "description": "Write 3 things grateful for", "category": "Gratitude", "progress": 55, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
    ],
    "habits": [
        {"id": "ha1", "domain_id": "habits", "title": "Morning routine", "description": "Wake up at 6am, exercise, shower", "category": "Morning Routine", "progress": 65, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "ha2", "domain_id": "habits", "title": "No social media before noon", "description": "Stay focused in the morning", "category": "Productivity", "progress": 40, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
    ],
    "relationships": [
        {"id": "r1", "domain_id": "relationships", "title": "Call parents weekly", "description": "Check in with parents every Sunday", "category": "Family", "progress": 85, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "r2", "domain_id": "relationships", "title": "Date night", "description": "Weekly date with partner", "category": "Partner", "progress": 100, "status": "completed", "target_date": None, "created_at": "2026-01-01T00:00:00"},
    ],
    "finance": [
        {"id": "f1", "domain_id": "finance", "title": "Save $1000/mo", "description": "Build emergency fund", "category": "Saving", "progress": 70, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
        {"id": "f2", "domain_id": "finance", "title": "Track expenses", "description": "Log all spending daily", "category": "Budgeting", "progress": 90, "status": "active", "target_date": None, "created_at": "2026-01-01T00:00:00"},
    ],
}

DEMO_PROGRESS = {
    "health":        {"total": 8,  "completed": 3, "active": 5, "streak": 12, "weekly_checkins": 5, "rate": 65},
    "career":        {"total": 5,  "completed": 1, "active": 4, "streak": 8,  "weekly_checkins": 4, "rate": 45},
    "mindset":       {"total": 6,  "completed": 2, "active": 4, "streak": 15, "weekly_checkins": 6, "rate": 72},
    "habits":        {"total": 10, "completed": 4, "active": 6, "streak": 23, "weekly_checkins": 7, "rate": 58},
    "relationships": {"total": 4,  "completed": 2, "active": 2, "streak": 6,  "weekly_checkins": 3, "rate": 80},
    "finance":       {"total": 6,  "completed": 2, "active": 4, "streak": 30, "weekly_checkins": 7, "rate": 85},
}


def _user_goals(user_id: str, domain_id: str) -> list:
    """Return the live goals list for a user+domain. Returns empty list for new users."""
    _goal_store.setdefault(user_id, {})
    if domain_id not in _goal_store[user_id]:
        # Don't auto-seed demo data - return empty list for new users
        _goal_store[user_id][domain_id] = []
    return _goal_store[user_id][domain_id]


def _user_checkins(user_id: str, domain_id: str) -> list:
    """Return the live check-ins list for a user+domain."""
    _checkin_store.setdefault(user_id, {})
    if domain_id not in _checkin_store[user_id]:
        _checkin_store[user_id][domain_id] = []
    return _checkin_store[user_id][domain_id]


def _user_snapshots(user_id: str) -> list:
    """Return the snapshots list for a user."""
    if user_id not in _snapshot_store:
        _snapshot_store[user_id] = []
    return _snapshot_store[user_id]


# ==================== MODELS ====================

class Domain(BaseModel):
    id: str
    name: str
    icon: str
    color: str
    description: str
    categories: List[str]


class DomainGoal(BaseModel):
    id: str
    domain_id: str
    title: str
    description: Optional[str] = None
    category: str
    progress: int = 0
    status: str = "active"
    target_date: Optional[str] = None
    created_at: str


class CreateGoalRequest(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_date: Optional[str] = None


class UpdateGoalRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None


class DailyCheckIn(BaseModel):
    id: str
    domain_id: str
    date: str
    status: str
    notes: Optional[str] = None
    metrics: Optional[dict] = None


class CheckInRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class DomainProgress(BaseModel):
    domain_id: str
    total_goals: int
    completed_goals: int
    active_goals: int
    current_streak: int
    weekly_checkins: int
    completion_rate: float


class DomainStats(BaseModel):
    domain_id: str
    goals_this_month: int
    completed_this_month: int
    checkins_this_week: int
    streak_days: int
    avg_progress: float


class RadarData(BaseModel):
    weeks: int
    series: List[dict]
    live: dict


class Snapshot(BaseModel):
    id: str
    domain_id: str
    week_start: str
    completion_rate: float
    active_goals: int
    completed_goals: int
    streak_days: int
    checkins_week: int


# ==================== HELPERS ====================

def _compute_progress(user_id: str, domain_id: str) -> DomainProgress:
    """Compute progress from goals + check-ins, falling back to demo data."""
    goals = _user_goals(user_id, domain_id)
    checkins = _user_checkins(user_id, domain_id)
    
    total = len(goals)
    completed = sum(1 for g in goals if g["status"] == "completed")
    active = sum(1 for g in goals if g["status"] == "active")
    weekly = sum(1 for c in checkins if c["status"] == "completed")
    
    avg_prog = sum(g["progress"] for g in goals) / total if total else 0
    
    # Compute streak
    streak = 0
    today = datetime.utcnow().date()
    checkin_dates = {datetime.fromisoformat(c["date"]).date() for c in checkins if c["status"] == "completed"}
    d = today
    while d in checkin_dates:
        streak += 1
        d -= timedelta(days=1)
    
    # Return actual progress - zeros for new users
    if total == 0:
        return DomainProgress(
            domain_id=domain_id,
            total_goals=0,
            completed_goals=0,
            active_goals=0,
            current_streak=0,
            weekly_checkins=0,
            completion_rate=0,
        )
    
    return DomainProgress(
        domain_id=domain_id,
        total_goals=total,
        completed_goals=completed,
        active_goals=active,
        current_streak=streak,
        weekly_checkins=weekly,
        completion_rate=round(avg_prog, 1),
    )


# ==================== READ ENDPOINTS ====================

@router.get("", response_model=List[Domain])
async def get_domains():
    """Get all life domains."""
    return list(DOMAINS.values())


@router.get("/progress/all")
async def get_all_progress(current_user: User = Depends(get_current_user)):
    """Get progress summary for all domains at once (used by the domains grid)."""
    result = {}
    for domain_id in DOMAINS:
        p = _compute_progress(str(current_user.id), domain_id)
        result[domain_id] = p.dict()
    return result


@router.get("/{domain_id}", response_model=Domain)
async def get_domain(domain_id: str):
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")
    return DOMAINS[domain_id]


@router.get("/{domain_id}/goals", response_model=List[DomainGoal])
async def get_domain_goals(
    domain_id: str,
    current_user: User = Depends(get_current_user)
):
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")
    return _user_goals(str(current_user.id), domain_id)


@router.get("/{domain_id}/progress", response_model=DomainProgress)
async def get_domain_progress(
    domain_id: str,
    current_user: User = Depends(get_current_user)
):
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")
    return _compute_progress(str(current_user.id), domain_id)


@router.get("/{domain_id}/checkins", response_model=List[DailyCheckIn])
async def get_domain_checkins(
    domain_id: str,
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user)
):
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")

    checkins = _user_checkins(str(current_user.id), domain_id)
    cutoff = (datetime.utcnow() - timedelta(days=days)).date()
    result = [c for c in checkins if datetime.fromisoformat(c["date"]).date() >= cutoff]

    # Return empty list for new users - no demo data
    if not result:
        return []
    return result


@router.get("/{domain_id}/stats", response_model=DomainStats)
async def get_domain_stats(
    domain_id: str,
    current_user: User = Depends(get_current_user)
):
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")
    goals = _user_goals(str(current_user.id), domain_id)
    checkins = _user_checkins(str(current_user.id), domain_id)
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0)
    week_ago = now - timedelta(days=6)

    goals_month = sum(1 for g in goals if datetime.fromisoformat(g["created_at"]) >= month_start)
    completed_month = sum(1 for g in goals if g["status"] == "completed" and datetime.fromisoformat(g["created_at"]) >= month_start)
    checkins_week = sum(1 for c in checkins if c["status"] == "completed" and datetime.fromisoformat(c["date"]) >= week_ago)
    avg_progress = round(sum(g["progress"] for g in goals) / len(goals), 1) if goals else 0

    p = _compute_progress(str(current_user.id), domain_id)
    return DomainStats(
        domain_id=domain_id,
        goals_this_month=goals_month,
        completed_this_month=completed_month,
        checkins_this_week=checkins_week,
        streak_days=p.current_streak,
        avg_progress=avg_progress,
    )


# ==================== WRITE ENDPOINTS ====================

@router.post("/{domain_id}/goals", response_model=DomainGoal, status_code=201)
async def create_domain_goal(
    domain_id: str,
    body: CreateGoalRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new goal in a domain."""
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")

    goal = {
        "id": str(uuid.uuid4()),
        "domain_id": domain_id,
        "title": body.title,
        "description": body.description,
        "category": body.category or DOMAINS[domain_id]["categories"][0],
        "progress": 0,
        "status": "active",
        "target_date": body.target_date,
        "created_at": datetime.utcnow().isoformat(),
    }
    _user_goals(str(current_user.id), domain_id).append(goal)
    return goal


@router.patch("/goals/{goal_id}", response_model=DomainGoal)
async def update_goal(
    goal_id: str,
    body: UpdateGoalRequest,
    current_user: User = Depends(get_current_user)
):
    """Update goal progress, status, or title."""
    uid = str(current_user.id)
    for domain_id in DOMAINS:
        goals = _user_goals(uid, domain_id)
        for goal in goals:
            if goal["id"] == goal_id:
                if body.progress is not None:
                    goal["progress"] = max(0, min(100, body.progress))
                    if goal["progress"] == 100:
                        goal["status"] = "completed"
                if body.status is not None:
                    goal["status"] = body.status
                if body.title is not None:
                    goal["title"] = body.title
                if body.description is not None:
                    goal["description"] = body.description
                return goal
    raise HTTPException(status_code=404, detail="Goal not found")


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a goal."""
    uid = str(current_user.id)
    for domain_id in DOMAINS:
        goals = _user_goals(uid, domain_id)
        original_len = len(goals)
        _goal_store[uid][domain_id] = [g for g in goals if g["id"] != goal_id]
        if len(_goal_store[uid][domain_id]) < original_len:
            return {"status": "deleted", "id": goal_id}
    raise HTTPException(status_code=404, detail="Goal not found")


@router.post("/{domain_id}/checkin", response_model=DailyCheckIn, status_code=201)
async def create_checkin(
    domain_id: str,
    body: CheckInRequest,
    current_user: User = Depends(get_current_user)
):
    """Log a daily check-in for a domain. One per day — upserts if called again."""
    if domain_id not in DOMAINS:
        raise HTTPException(status_code=404, detail="Domain not found")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    checkins = _user_checkins(str(current_user.id), domain_id)

    # Upsert: replace today's entry if it exists
    existing = next((i for i, c in enumerate(checkins) if c["date"] == today), None)
    entry = {
        "id": str(uuid.uuid4()),
        "domain_id": domain_id,
        "date": today,
        "status": body.status,
        "notes": body.notes,
        "metrics": None,
    }
    if existing is not None:
        checkins[existing] = entry
    else:
        checkins.append(entry)

    return entry


# ==================== SNAPSHOT ENDPOINTS ====================

def _get_week_start() -> str:
    """Get the Monday of the current ISO week."""
    today = datetime.utcnow().date()
    return (today - timedelta(days=today.weekday())).isoformat()


@router.get("/snapshots/radar")
async def get_radar_data(
    weeks: int = Query(8, ge=4, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get data for radar chart - series over time + live current scores."""
    uid = str(current_user.id)
    snapshots = _user_snapshots(uid)
    
    # Return empty series for new users - no demo data
    if not snapshots:
        series = []
    else:
        # Generate series data for each week
        series = []
        for w in range(weeks):
            week_start = (datetime.utcnow().date() - timedelta(weeks=w))
            week_start = week_start - timedelta(days=week_start.weekday())
            week_str = week_start.isoformat()
            
            # Try to find existing snapshot for this week
            week_snap = next((s for s in snapshots if s["week_start"] == week_str), None)
            
            if week_snap:
                series.append({
                    "week": week_str,
                    "data": {s["domain_id"]: s["completion_rate"] for s in snapshots if s["week_start"] == week_str}
                })
        
        series.reverse()
    
    # Live scores
    live = {}
    for domain_id in DOMAINS:
        p = _compute_progress(uid, domain_id)
        live[domain_id] = p.completion_rate
    
    return {"weeks": weeks, "series": series, "live": live}


@router.get("/snapshots/history")
async def get_snapshot_history(
    domain_id: Optional[str] = None,
    weeks: int = Query(8, ge=4, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get raw snapshot history, optionally filtered by domain."""
    uid = str(current_user.id)
    snapshots = _user_snapshots(uid)
    
    # Return empty history for new users
    if not snapshots:
        return []
    
    cutoff = (datetime.utcnow() - timedelta(weeks=weeks)).date()
    
    result = []
    for s in snapshots:
        week_date = datetime.fromisoformat(s["week_start"]).date()
        if week_date >= cutoff:
            if domain_id is None or s["domain_id"] == domain_id:
                result.append(s)
    
    result.sort(key=lambda x: x["week_start"])
    return result


@router.post("/snapshot")
async def trigger_snapshot(
    current_user: User = Depends(get_current_user)
):
    """Capture a snapshot for this week for all domains. Creates or updates the weekly snapshot."""
    uid = str(current_user.id)
    week_start = _get_week_start()
    snapshots = _user_snapshots(uid)
    
    # Remove existing snapshot for this week
    snapshots[:] = [s for s in snapshots if s["week_start"] != week_start]
    
    # Create new snapshots for each domain
    new_snapshots = []
    for domain_id in DOMAINS:
        p = _compute_progress(uid, domain_id)
        snapshot = {
            "id": str(uuid.uuid4()),
            "domain_id": domain_id,
            "week_start": week_start,
            "completion_rate": p.completion_rate,
            "active_goals": p.active_goals,
            "completed_goals": p.completed_goals,
            "streak_days": p.current_streak,
            "checkins_week": p.weekly_checkins,
        }
        snapshots.append(snapshot)
        new_snapshots.append(snapshot)
    
    return {"status": "captured", "week": week_start, "snapshots": new_snapshots}
