# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Demo mode for trying the platform without signup."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.models.user import User, SubscriptionTier

router = APIRouter(prefix="/demo", tags=["Demo Mode"])

# In-memory demo sessions
demo_sessions: dict[str, dict] = {}


# ==================== REQUEST/RESPONSE MODELS ====================

class DemoStartResponse(BaseModel):
    """Demo session response."""
    demo_token: str
    demo_user_id: str
    expires_at: str
    demo_features: dict


class DemoFeaturesResponse(BaseModel):
    """Demo features available."""
    features: dict


class DemoStatusResponse(BaseModel):
    """Demo session status."""
    is_demo: bool
    demo_expires_at: Optional[str] = None
    features: dict


# ==================== DEMO USER DATA ====================

DEMO_USER_DATA = {
    "id": "demo-user-001",
    "email": "demo@busybee.app",
    "full_name": "Demo User",
    "role": "user",
    "is_verified": True,
    "is_active": True,
    "subscription_tier": "pro",
    "avatar_url": None,
    "stripe_customer_id": None,
    "stripe_subscription_id": None,
    "oauth_provider": None,
    "oauth_id": None,
}


# ==================== DEMO FEATURES ====================

DEMO_FEATURES = {
    "executive_briefs": {
        "name": "Executive Briefs",
        "description": "Generate AI-powered executive briefs",
        "available": True,
        "limit": "unlimited"
    },
    "recommendations": {
        "name": "AI Recommendations",
        "description": "Get personalized AI recommendations",
        "available": True,
        "limit": "unlimited"
    },
    "domain_scoring": {
        "name": "Domain Scoring",
        "description": "Track scores across life domains",
        "available": True,
        "limit": "unlimited"
    },
    "decision_governance": {
        "name": "Decision Governance",
        "description": "Submit decisions for approval",
        "available": True,
        "limit": "unlimited"
    },
    "tree_of_life": {
        "name": "Tree of Life Engine",
        "description": "Graph-based orchestration (experimental)",
        "available": True,
        "limit": "unlimited"
    },
    "chat_assistant": {
        "name": "Chat Assistant",
        "description": "Chat with Busy Bee Chief of Staff",
        "available": True,
        "limit": "unlimited"
    },
    "export": {
        "name": "Data Export",
        "description": "Export your data",
        "available": False,
        "limit": "upgrade_required"
    },
    "api_access": {
        "name": "API Access",
        "description": "Programmatic access to platform",
        "available": False,
        "limit": "upgrade_required"
    }
}


# ==================== HELPER FUNCTIONS ====================

def create_demo_token() -> tuple[str, str]:
    """Create demo session token."""
    import secrets
    token = f"demo_{secrets.token_urlsafe(32)}"
    expires = datetime.utcnow() + timedelta(hours=24)
    return token, expires.isoformat()


# ==================== DEMO ROUTES ====================

@router.get("/features", response_model=DemoFeaturesResponse)
async def get_demo_features():
    """Get available demo features."""
    return DemoFeaturesResponse(features=DEMO_FEATURES)


@router.post("/start", response_model=DemoStartResponse)
async def start_demo_session():
    """Start a demo session."""
    
    token, expires_at = create_demo_token()
    demo_user_id = DEMO_USER_DATA["id"]
    
    # Store demo session
    demo_sessions[token] = {
        "demo_user_id": demo_user_id,
        "started_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at,
        "features": DEMO_FEATURES
    }
    
    return DemoStartResponse(
        demo_token=token,
        demo_user_id=demo_user_id,
        expires_at=expires_at,
        demo_features=DEMO_FEATURES
    )


@router.get("/status", response_model=DemoStatusResponse)
async def get_demo_status(demo_token: Optional[str] = None):
    """Get demo session status."""
    
    if not demo_token or demo_token not in demo_sessions:
        return DemoStatusResponse(
            is_demo=False,
            demo_expires_at=None,
            features={}
        )
    
    session = demo_sessions[demo_token]
    
    # Check if expired
    expires = datetime.fromisoformat(session["expires_at"])
    if expires < datetime.utcnow():
        del demo_sessions[demo_token]
        return DemoStatusResponse(
            is_demo=False,
            demo_expires_at=None,
            features={}
        )
    
    return DemoStatusResponse(
        is_demo=True,
        demo_expires_at=session["expires_at"],
        features=session["features"]
    )


@router.post("/end")
async def end_demo_session(demo_token: str):
    """End a demo session."""
    
    if demo_token in demo_sessions:
        del demo_sessions[demo_token]
        return {"message": "Demo session ended"}
    
    return {"message": "No active demo session"}


# ==================== DEMO AUTH (for testing) ====================

@router.get("/user", response_model=User)
async def get_demo_user(demo_token: Optional[str] = None):
    """Get demo user (for authenticated demo sessions)."""
    
    if not demo_token or demo_token not in demo_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid demo token required"
        )
    
    return User(**DEMO_USER_DATA)
