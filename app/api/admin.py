# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Admin dashboard API."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
import random

from app.models.user import User
from app.api.auth import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

# In-memory storage (replace with database)
# In production, these would be real database queries


# ==================== ENUMS ====================

class UserStatus(str, Enum):
    """User status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


# ==================== RESPONSE MODELS ====================

class PlatformStats(BaseModel):
    """Platform statistics."""
    total_users: int
    active_users_30d: int
    new_users_30d: int
    total_revenue: float
    mrr: float  # Monthly recurring revenue
    ARR: float  # Annual recurring revenue
    churn_rate: float
    avg_revenue_per_user: float


class UserMetrics(BaseModel):
    """User metrics."""
    total: int
    active: int
    inactive: int
    suspended: int
    by_plan: dict
    by_oauth_provider: dict
    growth: List[dict]


class RevenueMetrics(BaseModel):
    """Revenue metrics."""
    total_revenue: float
    mrr: float
    arr: float
    churn_rate: float
    ltv: float  # Lifetime value
    arpu: float  # Average revenue per user
    monthly_breakdown: List[dict]


class UserRow(BaseModel):
    """User row for admin table."""
    id: str
    email: str
    full_name: str
    role: str
    status: str
    plan: str
    created_at: str
    last_login: Optional[str]
    total_spent: float


class UsersListResponse(BaseModel):
    """Users list response."""
    users: List[UserRow]
    total: int
    page: int
    per_page: int


class TransactionRow(BaseModel):
    """Transaction row."""
    id: str
    user_id: str
    user_email: str
    amount: float
    currency: str
    status: str
    type: str
    description: str
    created_at: str


class TransactionsResponse(BaseModel):
    """Transactions response."""
    transactions: List[TransactionRow]
    total: int
    total_amount: float


class SystemHealth(BaseModel):
    """System health status."""
    status: str  # healthy, degraded, down
    uptime: float  # seconds
    api_response_time: float  # ms
    database_connected: bool
    external_services: dict


class FeatureUsage(BaseModel):
    """Feature usage stats."""
    feature_name: str
    active_users: int
    total_usage: int
    avg_per_user: float


class AdminSettings(BaseModel):
    """Platform admin settings."""
    platform_name: str
    support_email: str
    allow_signups: bool
    require_email_verification: bool
    maintenance_mode: bool
    features: dict


# ==================== PLATFORM STATS ====================

@router.get("/stats", dependencies=[Depends(require_admin)])
async def get_platform_stats(
    current_user: User = Depends(get_current_user)
):
    """Get platform-wide statistics."""
    
    return PlatformStats(
        total_users=1247,
        active_users_30d=892,
        new_users_30d=156,
        total_revenue=45678.90,
        mrr=12345.67,
        ARR=148148.04,
        churn_rate=2.3,
        avg_revenue_per_user=36.63
    )


@router.get("/metrics/users", dependencies=[Depends(require_admin)])
async def get_user_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get detailed user metrics."""
    
    return UserMetrics(
        total=1247,
        active=1089,
        inactive=142,
        suspended=16,
        by_plan={
            "free": 892,
            "pro": 312,
            "enterprise": 43
        },
        by_oauth_provider={
            "github": 456,
            "google": 389,
            "email": 402
        },
        growth=[
            {"date": "2026-01", "users": 1056},
            {"date": "2026-02", "users": 1134},
            {"date": "2026-03", "users": 1247}
        ]
    )


@router.get("/metrics/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get revenue metrics."""
    
    return RevenueMetrics(
        total_revenue=45678.90,
        mrr=12345.67,
        arr=148148.04,
        churn_rate=2.3,
        ltv=892.45,
        arpu=36.63,
        monthly_breakdown=[
            {"month": "2026-01", "revenue": 10234.56, "new_mrr": 1234.56},
            {"month": "2026-02", "revenue": 11456.78, "new_mrr": 1456.78},
            {"month": "2026-03", "revenue": 12345.67, "new_mrr": 1678.90}
        ]
    )


# ==================== USER MANAGEMENT ====================

@router.get("/users", dependencies=[Depends(require_admin)])
async def get_users(
    current_user: User = Depends(get_current_user),
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    plan: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all users (paginated)."""
    
    # Generate demo users
    users = []
    for i in range(per_page):
        users.append({
            "id": str(uuid.uuid4()),
            "email": f"user{i+1}@example.com",
            "full_name": f"User {i+1}",
            "role": "user",
            "status": random.choice(["active", "active", "active", "inactive"]),
            "plan": random.choice(["free", "free", "pro", "enterprise"]),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
            "last_login": (datetime.utcnow() - timedelta(hours=random.randint(1, 72))).isoformat(),
            "total_spent": round(random.uniform(0, 500), 2)
        })
    
    return UsersListResponse(
        users=[UserRow(**u) for u in users],
        total=1247,
        page=page,
        per_page=per_page
    )


@router.get("/users/{user_id}", dependencies=[Depends(require_admin)])
async def get_user_details(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user details."""
    
    return {
        "id": user_id,
        "email": "user@example.com",
        "full_name": "Example User",
        "role": "user",
        "status": "active",
        "plan": "pro",
        "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "last_login": datetime.utcnow().isoformat(),
        "subscription": {
            "plan": "pro",
            "status": "active",
            "current_period_end": (datetime.utcnow() + timedelta(days=15)).isoformat(),
            "cancel_at_period_end": False
        },
        "activity": {
            "goals_created": 5,
            "goals_completed": 2,
            "recommendations_completed": 12,
            "last_activity": datetime.utcnow().isoformat()
        },
        "billing": {
            "total_spent": 145.00,
            "transactions": 3
        }
    }


@router.patch("/users/{user_id}/status", dependencies=[Depends(require_admin)])
async def update_user_status(
    user_id: str,
    status: str,
    current_user: User = Depends(get_current_user)
):
    """Update user status."""
    
    valid_statuses = ["active", "inactive", "suspended"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Valid: {valid_statuses}"
        )
    
    return {"message": f"User status updated to {status}", "user_id": user_id}


@router.patch("/users/{user_id}/role", dependencies=[Depends(require_admin)])
async def update_user_role(
    user_id: str,
    role: str,
    current_user: User = Depends(get_current_user)
):
    """Update user role."""
    
    valid_roles = ["user", "admin", "moderator"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Valid: {valid_roles}"
        )
    
    return {"message": f"User role updated to {role}", "user_id": user_id}


# ==================== BILLING MANAGEMENT ====================

@router.get("/transactions", dependencies=[Depends(require_admin)])
async def get_all_transactions(
    current_user: User = Depends(get_current_user),
    page: int = 1,
    per_page: int = 20
):
    """Get all transactions."""
    
    transactions = []
    for i in range(per_page):
        transactions.append({
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "user_email": f"user{i+1}@example.com",
            "amount": round(random.uniform(9.99, 299.99), 2),
            "currency": "USD",
            "status": "succeeded",
            "type": random.choice(["subscription", "one_time"]),
            "description": "Pro Plan - Monthly",
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    total = sum(t["amount"] for t in transactions)
    
    return TransactionsResponse(
        transactions=[TransactionRow(**t) for t in transactions],
        total=1247,
        total_amount=round(total, 2)
    )


# ==================== SYSTEM HEALTH ====================

@router.get("/health", dependencies=[Depends(require_admin)])
async def get_system_health(
    current_user: User = Depends(get_current_user)
):
    """Get system health status."""
    
    return SystemHealth(
        status="healthy",
        uptime=86400.0,
        api_response_time=45.2,
        database_connected=True,
        external_services={
            "stripe": "healthy",
            "plaid": "healthy",
            "sendgrid": "healthy",
            "openai": "healthy"
        }
    )


# ==================== FEATURE USAGE ====================

@router.get("/features/usage", dependencies=[Depends(require_admin)])
async def get_feature_usage(
    current_user: User = Depends(get_current_user)
):
    """Get feature usage statistics."""
    
    features = [
        {"feature_name": "Dashboard", "active_users": 892, "total_usage": 15420, "avg_per_user": 17.3},
        {"feature_name": "Goals", "active_users": 756, "total_usage": 8934, "avg_per_user": 11.8},
        {"feature_name": "Recommendations", "active_users": 678, "total_usage": 12456, "avg_per_user": 18.4},
        {"feature_name": "Finance/Plaid", "active_users": 234, "total_usage": 3456, "avg_per_user": 14.8},
        {"feature_name": "Onboarding", "active_users": 445, "total_usage": 2234, "avg_per_user": 5.0},
        {"feature_name": "Chat", "active_users": 567, "total_usage": 8934, "avg_per_user": 15.8},
    ]
    
    return [FeatureUsage(**f) for f in features]


# ==================== ADMIN SETTINGS ====================

@router.get("/settings", dependencies=[Depends(require_admin)])
async def get_admin_settings(
    current_user: User = Depends(get_current_user)
):
    """Get platform settings."""
    
    return AdminSettings(
        platform_name="Busy Bee Holdings LLC",
        support_email="support@busybee.app",
        allow_signups=True,
        require_email_verification=True,
        maintenance_mode=False,
        features={
            "plaid_integration": True,
            "ai_recommendations": True,
            "executive_briefs": True,
            "tree_of_life": True,
            "demo_mode": True,
            "two_factor": True
        }
    )


@router.patch("/settings", dependencies=[Depends(require_admin)])
async def update_admin_settings(
    settings: AdminSettings,
    current_user: User = Depends(get_current_user)
):
    """Update platform settings."""
    
    return {"message": "Settings updated"}


# ==================== WEBHOOKS ====================

class WebhookEndpoint(BaseModel):
    """Webhook endpoint."""
    id: str
    url: str
    events: List[str]
    active: bool
    created_at: str


@router.get("/webhooks", dependencies=[Depends(require_admin)])
async def get_webhooks(
    current_user: User = Depends(get_current_user)
):
    """Get webhook endpoints."""
    
    return {
        "webhooks": [
            {
                "id": str(uuid.uuid4()),
                "url": "https://example.com/webhook",
                "events": ["user.created", "subscription.created", "payment.succeeded"],
                "active": True,
                "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat()
            }
        ]
    }


@router.post("/webhooks", dependencies=[Depends(require_admin)])
async def create_webhook(
    url: str,
    events: List[str],
    current_user: User = Depends(get_current_user)
):
    """Create webhook endpoint."""
    
    webhook = {
        "id": str(uuid.uuid4()),
        "url": url,
        "events": events,
        "active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {"message": "Webhook created", "webhook": WebhookEndpoint(**webhook)}


@router.delete("/webhooks/{webhook_id}", dependencies=[Depends(require_admin)])
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete webhook endpoint."""
    
    return {"message": "Webhook deleted"}


# ==================== ANALYTICS ====================

@router.get("/analytics", dependencies=[Depends(require_admin)])
async def get_analytics(
    current_user: User = Depends(get_current_user),
    days: int = 30
):
    """Get platform analytics."""
    
    # Daily active users over time
    dau = [
        {"date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"), "users": random.randint(300, 500)}
        for i in range(days, 0, -1)
    ]
    
    # Revenue over time
    revenue = [
        {"date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"), "amount": round(random.uniform(300, 600), 2)}
        for i in range(days, 0, -1)
    ]
    
    return {
        "daily_active_users": dau,
        "revenue": revenue,
        "summary": {
            "total_page_views": 45678,
            "avg_session_duration": 324,  # seconds
            "bounce_rate": 32.5,
            "top_pages": [
                {"path": "/dashboard", "views": 12345},
                {"path": "/goals", "views": 8765},
                {"path": "/finance", "views": 6543},
                {"path": "/", "views": 5432}
            ]
        }
    }
