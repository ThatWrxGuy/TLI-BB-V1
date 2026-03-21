# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""User profile and settings API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import uuid
import random

from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile & Settings"])

# In-memory storage (replace with database)
user_settings_db: dict[str, dict] = {}


# ==================== ENUMS ====================

class NotificationChannel(str, Enum):
    """Notification channels."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    NONE = "none"


class Theme(str, Enum):
    """UI themes."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


# ==================== RESPONSE MODELS ====================

class ProfileResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    full_name: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: str
    timezone: str
    language: str
    created_at: str


class ProfileUpdateRequest(BaseModel):
    """Profile update request."""
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class SettingsResponse(BaseModel):
    """User settings response."""
    user_id: str
    theme: str
    language: str
    timezone: str
    notifications: dict
    privacy: dict
    security: dict
    two_factor_enabled: bool
    updated_at: str


class SettingsUpdateRequest(BaseModel):
    """Settings update request."""
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    notifications: Optional[dict] = None
    privacy: Optional[dict] = None


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str


class TwoFactorSetupResponse(BaseModel):
    """2FA setup response."""
    secret: str
    qr_code: str  # Base64 or URL
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request."""
    code: str


class TwoFactorResponse(BaseModel):
    """2FA status response."""
    enabled: bool
    method: Optional[str] = None
    backup_codes_enabled: bool


class EmailPreferences(BaseModel):
    """Email preferences."""
    marketing: bool = False
    product_updates: bool = True
    security_alerts: bool = True
    weekly_digest: bool = False
    monthly_report: bool = True


class NotificationPreferences(BaseModel):
    """Notification preferences."""
    email: EmailPreferences
    push: dict
    in_app: dict


class PrivacySettings(BaseModel):
    """Privacy settings."""
    profile_visibility: str = "private"  # public, private, friends
    show_activity: bool = True
    allow_indexing: bool = False
    share_analytics: bool = False


# ==================== PROFILE ROUTES ====================

@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user profile."""
    
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        display_name=current_user.full_name.split()[0] if current_user.full_name else "User",
        avatar_url=current_user.avatar_url,
        bio=None,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        timezone="UTC",
        language="en",
        created_at=current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at)
    )


@router.patch("")
async def update_profile(
    updates: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user profile."""
    
    # In production, update database
    return {
        "message": "Profile updated",
        "updates": updates.model_dump(exclude_none=True)
    }


@router.get("/avatar")
async def get_avatar(
    current_user: User = Depends(get_current_user)
):
    """Get user avatar URL."""
    
    # Use Gravatar or uploaded avatar
    return {
        "avatar_url": current_user.avatar_url or f"https://api.dicebear.com/7.x/initials/svg?seed={current_user.email}",
        "uploaded_avatar": current_user.avatar_url is not None
    }


@router.post("/avatar")
async def upload_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user)
):
    """Upload/set avatar URL."""
    
    return {
        "message": "Avatar updated",
        "avatar_url": avatar_url
    }


# ==================== SETTINGS ROUTES ====================

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user)
):
    """Get user settings."""
    
    user_id = current_user.id
    
    # Get or create default settings
    if user_id not in user_settings_db:
        user_settings_db[user_id] = {
            "theme": "system",
            "language": "en",
            "timezone": "UTC",
            "notifications": {
                "email": {
                    "marketing": False,
                    "product_updates": True,
                    "security_alerts": True,
                    "weekly_digest": False,
                    "monthly_report": True
                },
                "push": {
                    "goals": True,
                    "recommendations": True,
                    "reminders": True,
                    "social": False
                },
                "in_app": {
                    "goals": True,
                    "recommendations": True,
                    "reminders": True,
                    "updates": True
                }
            },
            "privacy": {
                "profile_visibility": "private",
                "show_activity": True,
                "allow_indexing": False,
                "share_analytics": False
            },
            "security": {
                "two_factor_enabled": False,
                "two_factor_method": None,
                "backup_codes_enabled": False,
                "last_password_change": None,
                "active_sessions": 1
            },
            "updated_at": datetime.utcnow().isoformat()
        }
    
    settings = user_settings_db[user_id]
    
    return SettingsResponse(
        user_id=user_id,
        theme=settings["theme"],
        language=settings["language"],
        timezone=settings["timezone"],
        notifications=settings["notifications"],
        privacy=settings["privacy"],
        security=settings["security"],
        two_factor_enabled=settings["security"]["two_factor_enabled"],
        updated_at=settings["updated_at"]
    )


@router.patch("/settings")
async def update_settings(
    updates: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user settings."""
    
    user_id = current_user.id
    
    if user_id not in user_settings_db:
        user_settings_db[user_id] = {
            "theme": "system",
            "language": "en",
            "timezone": "UTC",
            "notifications": {},
            "privacy": {},
            "security": {}
        }
    
    # Apply updates
    if updates.theme:
        user_settings_db[user_id]["theme"] = updates.theme
    if updates.language:
        user_settings_db[user_id]["language"] = updates.language
    if updates.timezone:
        user_settings_db[user_id]["timezone"] = updates.timezone
    if updates.notifications:
        user_settings_db[user_id]["notifications"].update(updates.notifications)
    if updates.privacy:
        user_settings_db[user_id]["privacy"].update(updates.privacy)
    
    user_settings_db[user_id]["updated_at"] = datetime.utcnow().isoformat()
    
    return {"message": "Settings updated"}


@router.post("/settings/email-preferences")
async def update_email_preferences(
    preferences: EmailPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update email preferences."""
    
    user_id = current_user.id
    
    if user_id not in user_settings_db:
        user_settings_db[user_id] = {}
    
    if "notifications" not in user_settings_db[user_id]:
        user_settings_db[user_id]["notifications"] = {}
    
    user_settings_db[user_id]["notifications"]["email"] = preferences.model_dump()
    
    return {"message": "Email preferences updated"}


@router.post("/settings/notification-preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user)
):
    """Update all notification preferences."""
    
    user_id = current_user.id
    
    if user_id not in user_settings_db:
        user_settings_db[user_id] = {}
    
    user_settings_db[user_id]["notifications"] = {
        "email": preferences.email.model_dump(),
        "push": preferences.push,
        "in_app": preferences.in_app
    }
    
    return {"message": "Notification preferences updated"}


@router.post("/settings/privacy")
async def update_privacy_settings(
    privacy: PrivacySettings,
    current_user: User = Depends(get_current_user)
):
    """Update privacy settings."""
    
    user_id = current_user.id
    
    if user_id not in user_settings_db:
        user_settings_db[user_id] = {}
    
    user_settings_db[user_id]["privacy"] = privacy.model_dump()
    
    return {"message": "Privacy settings updated"}


# ==================== SECURITY ROUTES ====================

@router.post("/password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """Change password."""
    
    # TODO: Verify current password and hash new password
    # from passlib.context import CryptContext
    # pwd_context.verify(request.current_password, user.password_hash)
    
    return {"message": "Password changed successfully"}


# ==================== TWO-FACTOR AUTH ====================

@router.get("/two-factor/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    current_user: User = Depends(get_current_user)
):
    """Set up two-factor authentication."""
    
    # TODO: Use pyotp for TOTP
    # import pyotp
    # secret = pyotp.random_base32()
    # totp = pyotp.TOTP(secret)
    # qr_code = totp.provisioning_uri(user.email, issuer_name="Busy Bee")
    
    # Demo response
    import secrets
    secret = secrets.token_hex(20)
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
    
    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=otpauth://totp/Busy%20Bee:{current_user.email}?secret={secret}",
        backup_codes=backup_codes
    )


@router.post("/two-factor/enable")
async def enable_two_factor(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Enable two-factor authentication after verification."""
    
    # TODO: Verify the code using pyotp
    # import pyotp
    # totp = pyotp.TOTP(secret)
    # if not totp.verify(request.code):
    #     raise HTTPException(status_code=400, detail="Invalid code")
    
    user_id = current_user.id
    
    if user_id not in user_settings_db:
        user_settings_db[user_id] = {}
    
    if "security" not in user_settings_db[user_id]:
        user_settings_db[user_id]["security"] = {}
    
    user_settings_db[user_id]["security"]["two_factor_enabled"] = True
    user_settings_db[user_id]["security"]["two_factor_method"] = "totp"
    
    return {"message": "Two-factor authentication enabled"}


@router.post("/two-factor/disable")
async def disable_two_factor(
    current_user: User = Depends(get_current_user)
):
    """Disable two-factor authentication (opt-out)."""
    
    user_id = current_user.id
    
    if user_id in user_settings_db and "security" in user_settings_db[user_id]:
        user_settings_db[user_id]["security"]["two_factor_enabled"] = False
    
    return {"message": "Two-factor authentication disabled (opted out)"}


@router.get("/two-factor/status", response_model=TwoFactorResponse)
async def get_two_factor_status(
    current_user: User = Depends(get_current_user)
):
    """Get two-factor authentication status."""
    
    user_id = current_user.id
    
    enabled = False
    method = None
    backup_enabled = False
    
    if user_id in user_settings_db and "security" in user_settings_db[user_id]:
        enabled = user_settings_db[user_id]["security"].get("two_factor_enabled", False)
        method = user_settings_db[user_id]["security"].get("two_factor_method")
        backup_enabled = user_settings_db[user_id]["security"].get("backup_codes_enabled", False)
    
    return TwoFactorResponse(
        enabled=enabled,
        method=method,
        backup_codes_enabled=backup_enabled
    )


@router.post("/two-factor/backup-codes")
async def generate_backup_codes(
    current_user: User = Depends(get_current_user)
):
    """Generate new backup codes."""
    
    import secrets
    backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
    
    return {
        "backup_codes": backup_codes,
        "message": "New backup codes generated. Save these in a safe place."
    }


# ==================== SESSIONS ====================

class SessionInfo(BaseModel):
    """Session information."""
    id: str
    device: str
    ip_address: str
    location: str
    last_active: str
    current: bool


@router.get("/sessions", response_model=List[SessionInfo])
async def get_sessions(
    current_user: User = Depends(get_current_user)
):
    """Get active sessions."""
    
    # Demo sessions
    sessions = [
        {
            "id": str(uuid.uuid4()),
            "device": "Chrome on MacOS",
            "ip_address": "192.168.1.1",
            "location": "San Francisco, CA",
            "last_active": datetime.utcnow().isoformat(),
            "current": True
        },
        {
            "id": str(uuid.uuid4()),
            "device": "Safari on iPhone",
            "ip_address": "192.168.1.2",
            "location": "San Francisco, CA",
            "last_active": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "current": False
        }
    ]
    
    return [SessionInfo(**s) for s in sessions]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Revoke a session."""
    
    return {"message": "Session revoked"}


# ==================== DATA EXPORT ====================

@router.post("/export")
async def request_data_export(
    current_user: User = Depends(get_current_user)
):
    """Request data export (GDPR compliance)."""
    
    # In production, queue async job to generate export
    return {
        "message": "Data export requested",
        "export_id": str(uuid.uuid4()),
        "estimated_time": "5 minutes",
        "formats": ["JSON", "CSV"]
    }


@router.get("/export/{export_id}")
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get data export status."""
    
    return {
        "export_id": export_id,
        "status": "ready",  # pending, processing, ready, expired
        "download_url": f"/profile/download/{export_id}",
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }


@router.get("/download/{export_id}")
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download exported data."""
    
    # Return actual file in production
    return {
        "message": "Download ready",
        "data": {
            "profile": {},
            "goals": [],
            "transactions": [],
            "settings": {}
        }
    }


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user)
):
    """Delete account (with confirmation)."""
    
    return {
        "message": "Account deletion scheduled",
        "confirm_by": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "action": "Click confirmation link in email to permanently delete"
    }


# Import timedelta for sessions
from datetime import timedelta
