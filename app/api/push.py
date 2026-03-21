# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Push Notification Backend
   app/api/push.py

   Handles:
     - Subscription storage / removal
     - Sending pushes from the server (via pywebpush)
     - Nightly check-in reminder cron
     - AI goal suggestion trigger

   Install:
     pip install pywebpush

   Env vars (.env):
     VAPID_PRIVATE_KEY=...
     VAPID_PUBLIC_KEY=...
     VAPID_EMAIL=mailto:you@busybee.app

   Generate keys:
     python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print(v.private_key, v.public_key)"
   OR:
     npx web-push generate-vapid-keys
"""

from __future__ import annotations

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Text, DateTime
from pywebpush import webpush, WebPushException

from app.models.database import Base, User, get_db
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/push", tags=["Push Notifications"])

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY  = os.getenv("VAPID_PUBLIC_KEY",  "")
VAPID_EMAIL       = os.getenv("VAPID_EMAIL",        "mailto:admin@busybee.app")

DOMAIN_EMOJIS = {
    "health": "🏃", "career": "💼", "mindset": "🧠",
    "habits": "🔄", "relationships": "👥", "finance": "💰",
}


# ─── DB Model ─────────────────────────────────────────────────────────────────

class PushSubscription(Base):
    """Stores web push subscriptions per user."""
    __tablename__ = "push_subscriptions"

    id:          str = Column(String(36), primary_key=True)
    user_id:     str = Column(String(36), nullable=False, index=True)
    endpoint:    str = Column(Text, nullable=False, unique=True)
    p256dh:      str = Column(Text, nullable=False)
    auth:        str = Column(Text, nullable=False)
    created_at:  datetime = Column(DateTime, default=datetime.utcnow)
    last_used:   datetime = Column(DateTime, nullable=True)

    def to_subscription_info(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "keys": { "p256dh": self.p256dh, "auth": self.auth },
        }


# ─── Alembic migration snippet (add to your migration file) ──────────────────
# op.create_table("push_subscriptions",
#   sa.Column("id",         sa.String(36), primary_key=True),
#   sa.Column("user_id",    sa.String(36), nullable=False),
#   sa.Column("endpoint",   sa.Text(),     nullable=False, unique=True),
#   sa.Column("p256dh",     sa.Text(),     nullable=False),
#   sa.Column("auth",       sa.Text(),     nullable=False),
#   sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
#   sa.Column("last_used",  sa.DateTime(), nullable=True),
# )
# op.create_index("ix_push_subs_user_id", "push_subscriptions", ["user_id"])


# ─── Pydantic ─────────────────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    endpoint: str
    keys: dict  # { p256dh, auth }

class UnsubscribeRequest(BaseModel):
    endpoint: str

class PushPayload(BaseModel):
    title: str
    body: str
    url: Optional[str] = "/"
    tag: Optional[str] = "busy-bee"
    actions: Optional[list] = []


# ─── Core send helper ─────────────────────────────────────────────────────────

def _send_push(subscription_info: dict, payload: dict) -> bool:
    """Send a single push. Returns True on success, False on expired/invalid."""
    if not VAPID_PRIVATE_KEY:
        logger.warning("VAPID_PRIVATE_KEY not set — push skipped")
        return False
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_EMAIL},
        )
        return True
    except WebPushException as e:
        if e.response and e.response.status_code in (404, 410):
            return False   # subscription expired — caller should delete it
        logger.error(f"WebPush error: {e}")
        return False


def send_push_to_user(user_id: str, payload: dict, db: Session):
    """Send push to all subscriptions for a user. Cleans up expired ones."""
    import uuid as _uuid
    subs = db.query(PushSubscription).filter_by(user_id=user_id).all()
    for sub in subs:
        ok = _send_push(sub.to_subscription_info(), payload)
        if ok:
            sub.last_used = datetime.utcnow()
        else:
            db.delete(sub)
    db.commit()


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/subscribe", status_code=201)
async def subscribe(
    body: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import uuid as _uuid
    existing = db.query(PushSubscription).filter_by(endpoint=body.endpoint).first()
    if existing:
        existing.p256dh = body.keys.get("p256dh", "")
        existing.auth   = body.keys.get("auth",   "")
        db.commit()
        return {"status": "updated"}

    sub = PushSubscription(
        id=str(_uuid.uuid4()),
        user_id=str(current_user.id),
        endpoint=body.endpoint,
        p256dh=body.keys.get("p256dh", ""),
        auth=body.keys.get("auth",   ""),
    )
    db.add(sub)
    db.commit()

    # Welcome push
    send_push_to_user(str(current_user.id), {
        "title": "🐝 Busy Bee Notifications On",
        "body":  "You'll get a gentle nudge if you forget to check in. You can turn this off any time.",
        "url":   "/settings",
        "tag":   "welcome",
    }, db)

    return {"status": "subscribed"}


@router.post("/unsubscribe")
async def unsubscribe(
    body: UnsubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(PushSubscription).filter_by(
        endpoint=body.endpoint, user_id=str(current_user.id)
    ).first()
    if sub:
        db.delete(sub)
        db.commit()
    return {"status": "unsubscribed"}


@router.get("/status")
async def push_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = db.query(PushSubscription).filter_by(user_id=str(current_user.id)).count()
    return {"subscribed_devices": count, "vapid_configured": bool(VAPID_PRIVATE_KEY)}


@router.post("/test")
async def test_push(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a test push to the current user's devices."""
    send_push_to_user(str(current_user.id), {
        "title": "🐝 Test Notification",
        "body":  "Push notifications are working!",
        "url":   "/domains",
        "tag":   "test",
    }, db)
    return {"status": "sent"}


# ─── Nightly Check-In Reminder ────────────────────────────────────────────────
# Wire this into your scheduler at ~8 PM user time (or just call it from a cron endpoint)
# POST /push/remind-checkins  (call from cron, protected by a secret header)

@router.post("/remind-checkins")
async def remind_checkins(
    db: Session = Depends(get_db),
):
    """
    For every user who has push subscriptions but hasn't checked into ANY domain today,
    send a friendly reminder push with quick-action buttons.

    Secure this endpoint! Add a shared secret header check in production:
      if request.headers.get("X-Cron-Secret") != os.getenv("CRON_SECRET"): raise 403
    """
    from app.models.domain_models import DomainCheckIn

    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Get all users who have push subs
    subscribed_user_ids = db.query(PushSubscription.user_id).distinct().all()
    subscribed_user_ids = [r[0] for r in subscribed_user_ids]

    sent = 0
    for user_id in subscribed_user_ids:
        # Check if they've done ANY check-in today
        checkin_today = db.query(DomainCheckIn).filter(
            DomainCheckIn.user_id == user_id,
            DomainCheckIn.date    == today,
            DomainCheckIn.status  == "completed",
        ).first()

        if not checkin_today:
            send_push_to_user(user_id, {
                "title":   "🐝 Daily Check-In",
                "body":    "You haven't checked in today. 5 seconds is all it takes to keep your streak alive.",
                "url":     "/domains",
                "tag":     "daily-checkin",
                "actions": [
                    { "action": "checkin", "title": "✅ Check In Now" },
                    { "action": "dismiss", "title": "Later" },
                ],
            }, db)
            sent += 1

    logger.info(f"Sent {sent} check-in reminders")
    return {"sent": sent, "date": today}


# ─── AI Goal Suggestion Push ──────────────────────────────────────────────────

@router.post("/suggest-goals/{user_id}")
async def push_goal_suggestion(
    user_id: str,
    db: Session = Depends(get_db),
):
    """Called by the AI suggestion engine after generating suggestions for a user.
    Sends a push directing them to the weak domain."""
    # This is called programmatically — the AI backend populates domain_id + suggestion
    # See ai_suggestions.py for full flow
    pass  # implemented via send_push_to_user from ai_suggestions.py
