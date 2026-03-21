# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Push notifications API."""

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

router = APIRouter(prefix="/notifications", tags=["Push Notifications"])

# In-memory storage (replace with database)
push_tokens_db: dict[str, list[dict]] = {}
sent_notifications_db: dict[str, list[dict]] = {}


# ==================== ENUMS ====================

class NotificationPriority(str, Enum):
    """Notification priority."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationType(str, Enum):
    """Notification types."""
    GOAL = "goal"
    RECOMMENDATION = "recommendation"
    REMINDER = "reminder"
    SYSTEM = "system"
    MARKETING = "marketing"
    SECURITY = "security"
    SOCIAL = "social"


# ==================== RESPONSE MODELS ====================

class PushToken(BaseModel):
    """Push notification token."""
    id: str
    token: str
    device_type: str  # ios, android, web
    device_name: str
    created_at: str
    is_active: bool = True


class PushTokensResponse(BaseModel):
    """Push tokens response."""
    tokens: List[PushToken]
    count: int


class SendPushRequest(BaseModel):
    """Send push notification request."""
    title: str
    body: str
    priority: str = "normal"
    notification_type: str = "system"
    data: Optional[dict] = None
    schedule_at: Optional[str] = None  # ISO datetime for scheduled


class PushNotification(BaseModel):
    """Push notification record."""
    id: str
    title: str
    body: str
    priority: str
    type: str
    sent_at: str
    delivered: bool = False
    clicked: bool = False


class NotificationHistoryResponse(BaseModel):
    """Notification history response."""
    notifications: List[PushNotification]
    total: int
    unread: int


class PushSettings(BaseModel):
    """Push notification settings."""
    enabled: bool = True
    goal_reminders: bool = True
    recommendation_alerts: bool = True
    marketing: bool = False
    security_alerts: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


# ==================== DEVICE REGISTRATION ====================

@router.get("/push-tokens", response_model=PushTokensResponse)
async def get_push_tokens(
    current_user: User = Depends(get_current_user)
):
    """Get registered push tokens."""
    
    user_id = current_user.id
    
    if user_id not in push_tokens_db:
        # Demo tokens
        push_tokens_db[user_id] = [
            {
                "id": str(uuid.uuid4()),
                "token": "example-push-token-12345",
                "device_type": "ios",
                "device_name": "iPhone 14",
                "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "is_active": True
            }
        ]
    
    tokens = [t for t in push_tokens_db[user_id] if t["is_active"]]
    
    return PushTokensResponse(
        tokens=[PushToken(**t) for t in tokens],
        count=len(tokens)
    )


@router.post("/push-tokens")
async def register_push_token(
    token: str,
    device_type: str = "web",
    device_name: str = "Unknown Device",
    current_user: User = Depends(get_current_user)
):
    """Register a push notification token."""
    
    valid_types = ["ios", "android", "web"]
    if device_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid device type. Valid: {valid_types}"
        )
    
    user_id = current_user.id
    
    if user_id not in push_tokens_db:
        push_tokens_db[user_id] = []
    
    # Check if token already exists
    for existing in push_tokens_db[user_id]:
        if existing["token"] == token:
            existing["is_active"] = True
            existing["device_name"] = device_name
            return {"message": "Token updated", "token_id": existing["id"]}
    
    # Add new token
    new_token = {
        "id": str(uuid.uuid4()),
        "token": token,
        "device_type": device_type,
        "device_name": device_name,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }
    
    push_tokens_db[user_id].append(new_token)
    
    return {"message": "Token registered", "token_id": new_token["id"]}


@router.delete("/push-tokens/{token_id}")
async def unregister_push_token(
    token_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unregister a push token."""
    
    user_id = current_user.id
    
    if user_id not in push_tokens_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tokens found"
        )
    
    for token in push_tokens_db[user_id]:
        if token["id"] == token_id:
            token["is_active"] = False
            return {"message": "Token unregistered"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Token not found"
    )


# ==================== SEND NOTIFICATIONS ====================

@router.post("/send")
async def send_push_notification(
    request: SendPushRequest,
    current_user: User = Depends(get_current_user)
):
    """Send a push notification to current user."""
    
    user_id = current_user.id
    
    if user_id not in push_tokens_db or not any(t["is_active"] for t in push_tokens_db[user_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active push tokens"
        )
    
    # In production, use FCM/APNS to send
    # Example with Firebase Cloud Messaging:
    # import firebase_admin
    # from firebase_admin import messaging
    # message = messaging.Message(
    #     notification=messaging.Notification(
    #         title=request.title,
    #         body=request.body
    #     ),
    #     data=request.data or {},
    #     token=user_token
    # )
    # messaging.send(message)
    
    notification = {
        "id": str(uuid.uuid4()),
        "title": request.title,
        "body": request.body,
        "priority": request.priority,
        "type": request.notification_type,
        "sent_at": datetime.utcnow().isoformat(),
        "delivered": True,  # Demo
        "clicked": False
    }
    
    if user_id not in sent_notifications_db:
        sent_notifications_db[user_id] = []
    
    sent_notifications_db[user_id].append(notification)
    
    return {
        "message": "Notification sent",
        "notification_id": notification["id"],
        "recipients": 1
    }


# ==================== NOTIFICATION HISTORY ====================

@router.get("/history", response_model=NotificationHistoryResponse)
async def get_notification_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    unread_only: bool = False
):
    """Get notification history."""
    
    user_id = current_user.id
    
    # Generate demo notifications
    notifications = [
        {
            "id": str(uuid.uuid4()),
            "title": "Goal milestone! 🎉",
            "body": "You've reached 50% on your career goal",
            "priority": "high",
            "type": "goal",
            "sent_at": datetime.utcnow().isoformat(),
            "delivered": True,
            "clicked": False
        },
        {
            "id": str(uuid.uuid4()),
            "title": "New recommendation",
            "body": "Check out today's AI recommendation",
            "priority": "normal",
            "type": "recommendation",
            "sent_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "delivered": True,
            "clicked": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Reminder: Team meeting",
            "body": "Your 1:1 starts in 30 minutes",
            "priority": "high",
            "type": "reminder",
            "sent_at": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "delivered": True,
            "clicked": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Weekly digest",
            "body": "Here's your weekly progress summary",
            "priority": "low",
            "type": "system",
            "sent_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "delivered": True,
            "clicked": False
        }
    ]
    
    # Mark as read based on clicked
    for n in notifications:
        n["is_read"] = n["clicked"]
    
    if unread_only:
        notifications = [n for n in notifications if not n.get("is_read", False)]
    
    notifications = notifications[:limit]
    
    unread = sum(1 for n in notifications if not n.get("is_read", False))
    
    return NotificationHistoryResponse(
        notifications=[PushNotification(**n) for n in notifications],
        total=len(notifications),
        unread=unread
    )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read."""
    
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read."""
    
    return {"message": "All notifications marked as read"}


# ==================== PUSH SETTINGS ====================

@router.get("/settings", response_model=PushSettings)
async def get_push_settings(
    current_user: User = Depends(get_current_user)
):
    """Get push notification settings."""
    
    return PushSettings(
        enabled=True,
        goal_reminders=True,
        recommendation_alerts=True,
        marketing=False,
        security_alerts=True,
        quiet_hours_enabled=False,
        quiet_hours_start=None,
        quiet_hours_end=None
    )


@router.post("/settings")
async def update_push_settings(
    settings: PushSettings,
    current_user: User = Depends(get_current_user)
):
    """Update push notification settings."""
    
    return {"message": "Push settings updated"}


# ==================== BATCH NOTIFICATIONS (Admin) ====================

class BatchPushRequest(BaseModel):
    """Batch push notification request."""
    user_ids: Optional[List[str]] = None  # If empty, send to all
    segment: Optional[str] = None  # e.g., "all", "active", "premium"
    title: str
    body: str
    priority: str = "normal"
    notification_type: str = "system"


@router.post("/batch")
async def send_batch_push(
    request: BatchPushRequest,
    current_user: User = Depends(get_current_user)
):
    """Send push to multiple users (admin only in production)."""
    
    # Determine recipients
    if request.segment == "all":
        recipient_count = 1000  # Demo
    elif request.segment == "premium":
        recipient_count = 312
    elif request.user_ids:
        recipient_count = len(request.user_ids)
    else:
        recipient_count = 0
    
    return {
        "message": "Batch notification queued",
        "recipients": recipient_count,
        "estimated_delivery": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }
