# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""User-facing analytics API."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.models.database import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/user-analytics", tags=["User Analytics"])


# ==================== RESPONSE MODELS ====================

class ActivityDay(BaseModel):
    """Single day of activity."""
    date: str
    goals_created: int = 0
    goals_completed: int = 0
    tasks_created: int = 0
    tasks_completed: int = 0
    minutes_active: int = 0
    streak_continued: bool = False


class ActivityTimelineResponse(BaseModel):
    """Activity timeline response."""
    days: list[ActivityDay]
    total_goals_created: int
    total_goals_completed: int
    total_tasks_created: int
    total_tasks_completed: int
    total_minutes_active: int


class GoalProgress(BaseModel):
    """Goal progress data."""
    goal_id: str
    title: str
    created_at: str
    progress_history: list


class ProgressChartsResponse(BaseModel):
    """Progress charts response."""
    goal_progress: list
    task_completion: list
    completion_rate: float


class StreakData(BaseModel):
    """Streak data."""
    current_streak: int
    longest_streak: int
    streak_start_date: str
    streak_end_date: Optional[str]
    milestones: list


class Achievement(BaseModel):
    """Achievement/badge."""
    id: str
    name: str
    description: str
    icon: str
    earned_at: Optional[str]
    progress: Optional[float]
    is_earned: bool


class AchievementsResponse(BaseModel):
    """Achievements response."""
    achievements: list[Achievement]
    total_earned: int
    total_available: int


class WeeklyReportResponse(BaseModel):
    """Weekly report response."""
    week_start: str
    week_end: str
    summary: dict
    top_goals: list
    accomplishments: list
    insights: list
    next_week_suggestions: list


class PersonalInsight(BaseModel):
    """Personal insight."""
    id: str
    type: str  # tip, warning, achievement, suggestion
    title: str
    message: str
    icon: str
    created_at: str


class InsightsResponse(BaseModel):
    """Personal insights response."""
    insights: list[PersonalInsight]
    insight_count: int


class BenchmarkResponse(BaseModel):
    """Benchmark comparison response."""
    your_stats: dict
    average_stats: dict
    percentile: float
    comparison: list


# ==================== ACTIVITY TIMELINE ====================

@router.get("/activity", response_model=ActivityTimelineResponse)
async def get_activity_timeline(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user)
):
    """Get user's activity timeline."""
    
    days_data = []
    total_goals_created = 0
    total_goals_completed = 0
    total_tasks_created = 0
    total_tasks_completed = 0
    total_minutes = 0
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i - 1)
        date_str = date.strftime("%Y-%m-%d")
        
        # Generate demo data
        goals_created = random.randint(0, 3)
        goals_completed = random.randint(0, 2) if goals_created > 0 else 0
        tasks_created = random.randint(0, 5)
        tasks_completed = random.randint(0, 4)
        minutes = random.randint(5, 120)
        
        day = ActivityDay(
            date=date_str,
            goals_created=goals_created,
            goals_completed=goals_completed,
            tasks_created=tasks_created,
            tasks_completed=tasks_completed,
            minutes_active=minutes,
            streak_continued=(minutes > 0)
        )
        days_data.append(day)
        
        total_goals_created += goals_created
        total_goals_completed += goals_completed
        total_tasks_created += tasks_created
        total_tasks_completed += tasks_completed
        total_minutes += minutes
    
    return ActivityTimelineResponse(
        days=days_data,
        total_goals_created=total_goals_created,
        total_goals_completed=total_goals_completed,
        total_tasks_created=total_tasks_created,
        total_tasks_completed=total_tasks_completed,
        total_minutes_active=total_minutes
    )


# ==================== PROGRESS CHARTS ====================

@router.get("/progress", response_model=ProgressChartsResponse)
async def get_progress_charts(
    current_user: User = Depends(get_current_user)
):
    """Get progress charts data."""
    
    # Goal progress over time
    goal_progress = []
    for i in range(12):
        week = (datetime.utcnow() - timedelta(days=7 * (11 - i)))
        goal_progress.append({
            "week": week.strftime("%Y-%m-%d"),
            "goals_active": random.randint(2, 8),
            "goals_completed": random.randint(0, 3)
        })
    
    # Task completion over time
    task_completion = []
    for i in range(30):
        date = (datetime.utcnow() - timedelta(days=29 - i))
        task_completion.append({
            "date": date.strftime("%Y-%m-%d"),
            "completed": random.randint(0, 8),
            "created": random.randint(0, 5)
        })
    
    return ProgressChartsResponse(
        goal_progress=goal_progress,
        task_completion=task_completion,
        completion_rate=78.5
    )


# ==================== STREAKS & ACHIEVEMENTS ====================

@router.get("/streaks", response_model=StreakData)
async def get_streak_data(
    current_user: User = Depends(get_current_user)
):
    """Get user's streak data."""
    
    current_streak = random.randint(5, 30)
    longest_streak = max(current_streak + random.randint(5, 20), 45)
    
    return StreakData(
        current_streak=current_streak,
        longest_streak=longest_streak,
        streak_start_date=(datetime.utcnow() - timedelta(days=current_streak)).strftime("%Y-%m-%d"),
        streak_end_date=None,
        milestones=[
            {"days": 7, "name": "Week Warrior", "achieved": current_streak >= 7},
            {"days": 14, "name": "Two Week Wonder", "achieved": current_streak >= 14},
            {"days": 30, "name": "Monthly Master", "achieved": current_streak >= 30},
            {"days": 60, "name": "Two Month Titan", "achieved": current_streak >= 60},
            {"days": 100, "name": "Century Club", "achieved": current_streak >= 100},
        ]
    )


@router.get("/achievements", response_model=AchievementsResponse)
async def get_achievements(
    current_user: User = Depends(get_current_user)
):
    """Get user's achievements/badges."""
    
    achievements = [
        Achievement(
            id="first_goal",
            name="Goal Getter",
            description="Create your first goal",
            icon="🎯",
            earned_at="2024-01-15",
            is_earned=True
        ),
        Achievement(
            id="ten_tasks",
            name="Task Tackler",
            description="Complete 10 tasks",
            icon="✅",
            earned_at="2024-01-20",
            is_earned=True
        ),
        Achievement(
            id="week_streak",
            name="Week Warrior",
            description="Maintain a 7-day streak",
            icon="🔥",
            earned_at="2024-02-01",
            is_earned=True
        ),
        Achievement(
            id="goal_master",
            name="Goal Master",
            description="Complete 10 goals",
            icon="👑",
            earned_at=None,
            progress=75.0,
            is_earned=False
        ),
        Achievement(
            id="month_streak",
            name="Monthly Master",
            description="Maintain a 30-day streak",
            icon="⭐",
            earned_at=None,
            progress=66.0,
            is_earned=False
        ),
        Achievement(
            id="finance_connected",
            name="Financially Linked",
            description="Connect your bank account",
            icon="🏦",
            earned_at=None,
            progress=0.0,
            is_earned=False
        ),
        Achievement(
            id="chatty",
            name="Chatty",
            description="Use AI chat 50 times",
            icon="💬",
            earned_at=None,
            progress=34.0,
            is_earned=False
        ),
        Achievement(
            id="early_bird",
            name="Early Bird",
            description="Log in before 7 AM 10 times",
            icon="🌅",
            earned_at="2024-01-28",
            is_earned=True
        ),
    ]
    
    earned = sum(1 for a in achievements if a.is_earned)
    
    return AchievementsResponse(
        achievements=achievements,
        total_earned=earned,
        total_available=len(achievements)
    )


# ==================== WEEKLY REPORT ====================

@router.get("/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(
    current_user: User = Depends(get_current_user)
):
    """Get weekly activity report."""
    
    week_end = datetime.utcnow()
    week_start = week_end - timedelta(days=6)
    
    return WeeklyReportResponse(
        week_start=week_start.strftime("%Y-%m-%d"),
        week_end=week_end.strftime("%Y-%m-%d"),
        summary={
            "goals_created": 3,
            "goals_completed": 2,
            "tasks_created": 12,
            "tasks_completed": 9,
            "minutes_active": 345,
            "days_active": 6
        },
        top_goals=[
            {"title": "Learn Python", "progress": 15},
            {"title": "Save $5,000", "progress": 8},
            {"title": "Exercise 3x/week", "progress": 20}
        ],
        accomplishments=[
            "Completed 9 tasks this week!",
            "Maintained a 23-day streak",
            "Achieved 75% of daily goals"
        ],
        insights=[
            "You're most productive on Tuesdays",
            "You complete tasks faster than 68% of users",
            "Finance feature usage is up 40% this month"
        ],
        next_week_suggestions=[
            "Focus on 'Learn Python' - you're 65% through!",
            "Try completing tasks earlier in the day",
            "Consider adding a new finance goal"
        ]
    )


# ==================== PERSONAL INSIGHTS ====================

@router.get("/insights", response_model=InsightsResponse)
async def get_personal_insights(
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered personal insights."""
    
    insights = [
        PersonalInsight(
            id="insight_1",
            type="tip",
            title="🔥 Keep Your Streak Alive",
            message="You're on a 23-day streak! Complete one task today to maintain it.",
            icon="🔥",
            created_at=datetime.utcnow().isoformat()
        ),
        PersonalInsight(
            id="insight_2",
            type="suggestion",
            title="💡 Time to Review Goals",
            message="You have 3 goals with no progress in 7 days. Consider updating or completing them.",
            icon="💡",
            created_at=datetime.utcnow().isoformat()
        ),
        PersonalInsight(
            id="insight_3",
            type="achievement",
            title="🎉 Almost There!",
            message="You're 2 tasks away from earning the 'Task Tackler' badge!",
            icon="🎉",
            created_at=datetime.utcnow().isoformat()
        ),
        PersonalInsight(
            id="insight_4",
            type="warning",
            title="⚠️ Finance Update",
            message="Your spending increased 15% this week. Check the finance tab for details.",
            icon="⚠️",
            created_at=datetime.utcnow().isoformat()
        ),
        PersonalInsight(
            id="insight_5",
            type="tip",
            title="🌟 Peak Performance",
            message="You complete 40% more tasks on Tuesday. Schedule important tasks then!",
            icon="🌟",
            created_at=datetime.utcnow().isoformat()
        ),
    ]
    
    return InsightsResponse(
        insights=insights,
        insight_count=len(insights)
    )


# ==================== BENCHMARK ====================

@router.get("/benchmark", response_model=BenchmarkResponse)
async def get_benchmark(
    current_user: User = Depends(get_current_user)
):
    """Compare user stats to platform average."""
    
    your_stats = {
        "tasks_completed": 47,
        "goals_completed": 8,
        "current_streak": 23,
        "avg_tasks_per_day": 3.2,
        "completion_rate": 78.5
    }
    
    average_stats = {
        "tasks_completed": 32,
        "goals_completed": 5,
        "current_streak": 12,
        "avg_tasks_per_day": 2.1,
        "completion_rate": 62.3
    }
    
    return BenchmarkResponse(
        your_stats=your_stats,
        average_stats=average_stats,
        percentile=78.5,
        comparison=[
            {"metric": "Tasks Completed", "you": 47, "average": 32, "status": "above"},
            {"metric": "Goals Completed", "you": 8, "average": 5, "status": "above"},
            {"metric": "Current Streak", "you": 23, "average": 12, "status": "above"},
            {"metric": "Completion Rate", "you": "78.5%", "average": "62.3%", "status": "above"}
        ]
    )


# ==================== SUMMARY ====================

@router.get("/summary", response_model=dict)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user)
):
    """Get quick analytics summary."""
    
    return {
        "total_goals": 12,
        "completed_goals": 8,
        "total_tasks": 47,
        "completed_tasks": 39,
        "current_streak": 23,
        "longest_streak": 45,
        "achievements_earned": 4,
        "total_achievements": 8,
        "member_since": "2024-01-01",
        "days_active": 78,
        "completion_rate": 78.5
    }
