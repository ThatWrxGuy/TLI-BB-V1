# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""User onboarding questionnaire and flow."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid

from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# In-memory storage (replace with database)
onboarding_data: dict[str, dict] = {}


# ==================== ENUMS ====================

class OnboardingStep(str, Enum):
    """Onboarding steps."""
    WELCOME = "welcome"
    PROFILE = "profile"
    GOALS = "goals"
    PREFERENCES = "preferences"
    PLAN = "plan"
    COMPLETE = "complete"


class UserGoal(str, Enum):
    """User goals for the platform."""
    CAREER_GROWTH = "career_growth"
    FINANCIAL_INDEPENDENCE = "financial_independence"
    HEALTH_FITNESS = "health_fitness"
    RELATIONSHIPS = "relationships"
    PERSONAL_DEVELOPMENT = "personal_development"
    BUSINESS_BUILDING = "business_building"
    TIME_FREEDOM = "time_freedom"
    OTHER = "other"


class ExperienceLevel(str, Enum):
    """User experience level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class NotificationPreference(str, Enum):
    """Notification preferences."""
    EMAIL_DAILY = "email_daily"
    EMAIL_WEEKLY = "email_weekly"
    EMAIL_NEWSLETTER = "email_newsletter"
    PUSH_NOTIFICATIONS = "push_notifications"
    NONE = "none"


# ==================== REQUEST/RESPONSE MODELS ====================

class OnboardingStatusResponse(BaseModel):
    """Onboarding status response."""
    user_id: str
    current_step: str
    progress_percentage: int
    steps_completed: List[str]
    is_complete: bool


class ProfileAnswers(BaseModel):
    """Profile setup answers."""
    display_name: str
    role_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class GoalsAnswers(BaseModel):
    """Goals selection answers."""
    primary_goals: List[UserGoal]
    secondary_goals: Optional[List[UserGoal]] = None
    biggest_challenge: Optional[str] = None
    what_motivates: Optional[str] = None


class PreferencesAnswers(BaseModel):
    """Preferences answers."""
    experience_level: ExperienceLevel
    notification_preferences: List[NotificationPreference]
    timezone: str = "UTC"
    language: str = "en"


class PlanSelection(BaseModel):
    """Plan selection."""
    selected_tier: str  # free, pro, enterprise
    billing_cycle: Optional[str] = "monthly"  # monthly, yearly


# ==================== ONBOARDING STEPS ====================

ONBOARDING_FLOW = [
    {"step": "welcome", "title": "Welcome", "description": "Welcome to Busy Bee!"},
    {"step": "profile", "title": "Your Profile", "description": "Tell us about yourself"},
    {"step": "goals", "title": "Your Goals", "description": "What do you want to achieve?"},
    {"step": "preferences", "title": "Preferences", "description": "Customize your experience"},
    {"step": "plan", "title": "Choose Plan", "description": "Select your subscription"},
    {"step": "complete", "title": "Complete", "description": "You're all set!"},
]


def get_step_index(step: str) -> int:
    """Get index of step in flow."""
    for i, s in enumerate(ONBOARDING_FLOW):
        if s["step"] == step:
            return i
    return 0


# ==================== ROUTES ====================

@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """Get current onboarding status."""
    
    user_id = current_user.id
    
    if user_id not in onboarding_data:
        # Initialize onboarding
        onboarding_data[user_id] = {
            "user_id": user_id,
            "current_step": "welcome",
            "steps_completed": [],
            "profile": None,
            "goals": None,
            "preferences": None,
            "plan": None,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None
        }
    
    data = onboarding_data[user_id]
    current_step = data["current_step"]
    step_index = get_step_index(current_step)
    progress = int((step_index / (len(ONBOARDING_FLOW) - 1)) * 100)
    
    return OnboardingStatusResponse(
        user_id=user_id,
        current_step=current_step,
        progress_percentage=progress,
        steps_completed=data["steps_completed"],
        is_complete=data["current_step"] == "complete"
    )


@router.post("/profile")
async def submit_profile(
    answers: ProfileAnswers,
    current_user: User = Depends(get_current_user)
):
    """Submit profile information."""
    
    user_id = current_user.id
    
    if user_id not in onboarding_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Onboarding not started"
        )
    
    data = onboarding_data[user_id]
    
    if data["current_step"] not in ["welcome", "profile"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already submitted"
        )
    
    # Store profile
    data["profile"] = answers.model_dump()
    data["current_step"] = "goals"
    
    if "profile" not in data["steps_completed"]:
        data["steps_completed"].append("profile")
    
    return {
        "message": "Profile saved",
        "next_step": "goals",
        "next_step_title": "Your Goals"
    }


@router.post("/goals")
async def submit_goals(
    answers: GoalsAnswers,
    current_user: User = Depends(get_current_user)
):
    """Submit goals selection."""
    
    user_id = current_user.id
    
    if user_id not in onboarding_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Onboarding not started"
        )
    
    data = onboarding_data[user_id]
    
    if data["current_step"] not in ["profile", "goals"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goals already submitted"
        )
    
    # Store goals
    data["goals"] = answers.model_dump()
    data["current_step"] = "preferences"
    
    if "goals" not in data["steps_completed"]:
        data["steps_completed"].append("goals")
    
    return {
        "message": "Goals saved",
        "next_step": "preferences",
        "next_step_title": "Preferences"
    }


@router.post("/preferences")
async def submit_preferences(
    answers: PreferencesAnswers,
    current_user: User = Depends(get_current_user)
):
    """Submit preferences."""
    
    user_id = current_user.id
    
    if user_id not in onboarding_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Onboarding not started"
        )
    
    data = onboarding_data[user_id]
    
    if data["current_step"] not in ["goals", "preferences"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferences already submitted"
        )
    
    # Store preferences
    data["preferences"] = answers.model_dump()
    data["current_step"] = "plan"
    
    if "preferences" not in data["steps_completed"]:
        data["steps_completed"].append("preferences")
    
    return {
        "message": "Preferences saved",
        "next_step": "plan",
        "next_step_title": "Choose Plan"
    }


@router.post("/plan")
async def submit_plan(
    selection: PlanSelection,
    current_user: User = Depends(get_current_user)
):
    """Submit plan selection and complete onboarding."""
    
    user_id = current_user.id
    
    if user_id not in onboarding_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Onboarding not started"
        )
    
    data = onboarding_data[user_id]
    
    if data["current_step"] not in ["preferences", "plan"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan already selected"
        )
    
    # Store plan selection
    data["plan"] = selection.model_dump()
    data["current_step"] = "complete"
    data["steps_completed"].append("plan")
    data["completed_at"] = datetime.utcnow().isoformat()
    
    return {
        "message": "Onboarding complete!",
        "selected_tier": selection.selected_tier,
        "billing_cycle": selection.billing_cycle,
        "next_steps": [
            "Explore your dashboard",
            "Set up your first goal",
            "Try the AI assistant"
        ]
    }


@router.post("/skip")
async def skip_onboarding(
    current_user: User = Depends(get_current_user)
):
    """Skip onboarding and set defaults."""
    
    user_id = current_user.id
    
    # Set default onboarding data
    onboarding_data[user_id] = {
        "user_id": user_id,
        "current_step": "complete",
        "steps_completed": [],
        "profile": None,
        "goals": None,
        "preferences": None,
        "plan": None,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "skipped": True
    }
    
    return {
        "message": "Onboarding skipped",
        "next_step": "dashboard"
    }


@router.get("/questions/{step}")
async def get_questions_for_step(step: str):
    """Get questions for a specific step."""
    
    questions = {
        "welcome": {
            "title": "Welcome to Busy Bee! 🐝",
            "description": "Let's set up your personalized experience. This will take about 2 minutes.",
            "steps": [
                {"key": "profile", "label": "Your Profile", "icon": "👤"},
                {"key": "goals", "label": "Your Goals", "icon": "🎯"},
                {"key": "preferences", "label": "Preferences", "icon": "⚙️"},
                {"key": "plan", "label": "Choose Plan", "icon": "💎"},
            ]
        },
        "profile": {
            "title": "Tell us about yourself",
            "description": "This helps us personalize your experience.",
            "fields": [
                {"key": "display_name", "label": "Display Name", "type": "text", "required": True},
                {"key": "role_title", "label": "Your Role/Title", "type": "text", "required": False, "placeholder": "e.g., Software Engineer, CEO, Student"},
                {"key": "company", "label": "Company/Organization", "type": "text", "required": False, "placeholder": "e.g., Acme Inc"},
                {"key": "location", "label": "Location", "type": "text", "required": False, "placeholder": "e.g., San Francisco, CA"},
                {"key": "bio", "label": "Short Bio", "type": "textarea", "required": False, "placeholder": "Tell us a bit about yourself..."},
            ]
        },
        "goals": {
            "title": "What do you want to achieve?",
            "description": "Select your primary goals. You can change these anytime.",
            "fields": [
                {
                    "key": "primary_goals",
                    "label": "Primary Goals",
                    "type": "multi_select",
                    "required": True,
                    "options": [
                        {"value": "career_growth", "label": "Career Growth", "icon": "📈"},
                        {"value": "financial_independence", "label": "Financial Independence", "icon": "💰"},
                        {"value": "health_fitness", "label": "Health & Fitness", "icon": "💪"},
                        {"value": "relationships", "label": "Relationships", "icon": "❤️"},
                        {"value": "personal_development", "label": "Personal Development", "icon": "🌱"},
                        {"value": "business_building", "label": "Business Building", "icon": "🏢"},
                        {"value": "time_freedom", "label": "Time Freedom", "icon": "⏰"},
                        {"value": "other", "label": "Other", "icon": "✨"},
                    ]
                },
                {"key": "biggest_challenge", "label": "Biggest Challenge", "type": "textarea", "required": False, "placeholder": "What's your biggest challenge right now?"},
                {"key": "what_motivates", "label": "What motivates you?", "type": "textarea", "required": False, "placeholder": "What drives you to succeed?"},
            ]
        },
        "preferences": {
            "title": "Customize your experience",
            "description": "Set your preferences for notifications and display.",
            "fields": [
                {
                    "key": "experience_level",
                    "label": "Your Experience Level",
                    "type": "select",
                    "required": True,
                    "options": [
                        {"value": "beginner", "label": "Beginner - Just getting started"},
                        {"value": "intermediate", "label": "Intermediate - Some experience"},
                        {"value": "advanced", "label": "Advanced - Experienced user"},
                        {"value": "expert", "label": "Expert - Power user"},
                    ]
                },
                {
                    "key": "notification_preferences",
                    "label": "Notification Preferences",
                    "type": "multi_select",
                    "required": True,
                    "options": [
                        {"value": "email_daily", "label": "Daily Email Digest"},
                        {"value": "email_weekly", "label": "Weekly Summary"},
                        {"value": "email_newsletter", "label": "Monthly Newsletter"},
                        {"value": "push_notifications", "label": "Push Notifications"},
                        {"value": "none", "label": "No Notifications"},
                    ]
                },
                {"key": "timezone", "label": "Your Timezone", "type": "text", "required": True, "default": "UTC"},
                {"key": "language", "label": "Language", "type": "text", "required": True, "default": "en"},
            ]
        },
        "plan": {
            "title": "Choose your plan",
            "description": "Start free or upgrade for more features.",
            "plans": [
                {
                    "id": "free",
                    "name": "Free",
                    "price": "$0",
                    "period": "forever",
                    "features": [
                        "Basic AI recommendations",
                        "Executive briefs (limited)",
                        "Goal tracking",
                        "Community support"
                    ],
                    "cta": "Get Started Free"
                },
                {
                    "id": "pro",
                    "name": "Pro",
                    "price": "$29",
                    "period": "/month",
                    "features": [
                        "Everything in Free",
                        "Unlimited AI recommendations",
                        "Advanced analytics",
                        "Priority support",
                        "API access",
                        "Custom integrations"
                    ],
                    "cta": "Upgrade to Pro",
                    "popular": True
                },
                {
                    "id": "enterprise",
                    "name": "Enterprise",
                    "price": "$99",
                    "period": "/month",
                    "features": [
                        "Everything in Pro",
                        "Dedicated account manager",
                        "Custom SLAs",
                        "On-premise deployment",
                        "Advanced security",
                        "White-label options"
                    ],
                    "cta": "Contact Sales"
                }
            ]
        }
    }
    
    if step not in questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step '{step}' not found"
        )
    
    return questions[step]
