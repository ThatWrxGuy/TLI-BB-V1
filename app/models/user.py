# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""User model for authentication and billing."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
import uuid


class UserRole(str, Enum):
    """User roles in the system."""
    USER = "user"
    ADMIN = "admin"


class SubscriptionTier(str, Enum):
    """Subscription tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class OAuthProvider(str, Enum):
    """OAuth providers."""
    GITHUB = "github"
    GOOGLE = "google"


class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation request."""
    password: Optional[str] = None  # Required for email/password signup
    oauth_provider: Optional[OAuthProvider] = None
    oauth_id: Optional[str] = None


class UserUpdate(BaseModel):
    """User update request."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None


class User(UserBase):
    """User model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: UserRole = UserRole.USER
    is_verified: bool = False
    is_active: bool = True
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    oauth_provider: Optional[OAuthProvider] = None
    oauth_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    """User stored in database with password hash."""
    password_hash: Optional[str] = None
    verification_token: Optional[str] = None
    verification_expires: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[str] = None


class EmailVerification(BaseModel):
    """Email verification token payload."""
    user_id: str
    email: EmailStr
    expires_at: datetime


class PasswordReset(BaseModel):
    """Password reset token payload."""
    user_id: str
    expires_at: datetime


class Subscription(BaseModel):
    """User subscription details."""
    tier: SubscriptionTier
    status: str  # active, canceled, past_due, trialing
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
