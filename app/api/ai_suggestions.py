# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""AI Goal Suggestions Engine
   app/api/ai_suggestions.py

   Analyzes each user's domain progress and generates personalized goal
   suggestions for their 2 weakest domains using OpenAI GPT-4o-mini.

   Endpoints:
     GET  /suggestions                → get suggestions for current user
     POST /suggestions/generate       → (re)generate suggestions for current user
     POST /suggestions/generate-all   → admin: generate for all users (cron)

   Install:
     pip install openai

   Env vars:
     OPENAI_API_KEY=sk-...
"""

from __future__ import annotations

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Float, Integer
from sqlalchemy.orm import Session

from app.models.database import Base, User
from app.database import get_db
from app.api.auth import get_current_user
from app.api.push import send_push_to_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/suggestions", tags=["AI Suggestions"])

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL    = os.getenv("OPENAI_SUGGESTION_MODEL", "gpt-4o-mini")

DOMAIN_ORDER = ["health", "career", "mindset", "habits", "relationships", "finance"]
DOMAIN_CONTEXT = {
    "health":        "physical fitness, sleep, nutrition, medical care, mental health",
    "career":        "professional skills, career growth, business development, networking",
    "mindset":       "meditation, gratitude practice, journaling, self-improvement, reading",
    "habits":        "morning/evening routines, productivity systems, daily rituals",
    "relationships": "family time, friendships, romantic relationships, social connections",
    "finance":       "budgeting, saving, investing, income growth, debt reduction",
}
DOMAIN_EMOJIS = {
    "health": "🏃", "career": "💼", "mindset": "🧠",
    "habits": "🔄", "relationships": "👥", "finance": "💰",
}


# ─── DB Model ─────────────────────────────────────────────────────────────────

class GoalSuggestion(Base):
    """Cached AI-generated goal suggestions per user per domain."""
    __tablename__ = "goal_suggestions"

    id:              str      = Column(String(36), primary_key=True)
    user_id:         str      = Column(String(36), nullable=False, index=True)
    domain_id:       str      = Column(String(32), nullable=False)
    title:           str      = Column(String(255), nullable=False)
    description:     str      = Column(Text, nullable=True)
    category:        str      = Column(String(64), nullable=True)
    why:             str      = Column(Text, nullable=True)   # AI's reasoning
    difficulty:      str      = Column(String(16), nullable=True)  # easy / medium / hard
    domain_score:    float    = Column(Float, nullable=True)  # score at generation time
    accepted:        Optional[bool] = Column(String(5), nullable=True)  # "true"/"false"/None
    generated_at:    datetime = Column(DateTime, default=datetime.utcnow)
    expires_at:      datetime = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "domain_id":    self.domain_id,
            "title":        self.title,
            "description":  self.description,
            "category":     self.category,
            "why":          self.why,
            "difficulty":   self.difficulty,
            "domain_score": self.domain_score,
            "accepted":     self.accepted,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "expires_at":   self.expires_at.isoformat()   if self.expires_at   else None,
        }


# ─── Alembic migration snippet ────────────────────────────────────────────────
# op.create_table("goal_suggestions",
#   sa.Column("id",           sa.String(36),  primary_key=True),
#   sa.Column("user_id",      sa.String(36),  nullable=False),
#   sa.Column("domain_id",    sa.String(32),  nullable=False),
#   sa.Column("title",        sa.String(255), nullable=False),
#   sa.Column("description",  sa.Text(),      nullable=True),
#   sa.Column("category",     sa.String(64),  nullable=True),
#   sa.Column("why",          sa.Text(),      nullable=True),
#   sa.Column("difficulty",   sa.String(16),  nullable=True),
#   sa.Column("domain_score", sa.Float(),     nullable=True),
#   sa.Column("accepted",     sa.String(5),   nullable=True),
#   sa.Column("generated_at", sa.DateTime(),  server_default=sa.func.now()),
#   sa.Column("expires_at",   sa.DateTime(),  nullable=True),
# )
# op.create_index("ix_suggestions_user_id",  "goal_suggestions", ["user_id"])
# op.create_index("ix_suggestions_domain_id","goal_suggestions", ["domain_id"])


# ─── Pydantic ─────────────────────────────────────────────────────────────────

class SuggestionResponse(BaseModel):
    id: str; domain_id: str; title: str; description: Optional[str]
    category: Optional[str]; why: Optional[str]; difficulty: Optional[str]
    domain_score: Optional[float]; generated_at: str

class AcceptSuggestionRequest(BaseModel):
    accepted: bool


# ─── AI Generation ────────────────────────────────────────────────────────────

def _build_prompt(domain_id: str, domain_score: float, existing_goals: list, user_name: str = "the user") -> str:
    context = DOMAIN_CONTEXT.get(domain_id, domain_id)
    existing = ", ".join(f'"{g}"' for g in existing_goals[:5]) if existing_goals else "none yet"

    return f"""You are a personal life coach inside Busy Bee, a life management app.

User context:
- Domain: {domain_id.title()} ({context})
- Current domain score: {domain_score:.0f}/100 (this is their weak area)
- Existing goals in this domain: {existing}

Your task: Suggest 3 specific, achievable, motivating goals for this domain.
Each goal should be different in difficulty (one easy, one medium, one stretch).
Make them concrete and actionable — not vague.
Do NOT repeat existing goals.

Respond ONLY with valid JSON array, no markdown:
[
  {{
    "title": "Short actionable goal title",
    "description": "1-2 sentence description with specifics",
    "category": "one of the domain categories",
    "why": "one sentence — why this matters for their score",
    "difficulty": "easy" | "medium" | "hard"
  }},
  ...
]"""


def _call_openai(prompt: str) -> list:
    """Call OpenAI and parse the JSON response. Returns list of suggestion dicts."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        # GPT may wrap in {"suggestions": [...]} or return array directly
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        # Try common wrapper keys
        for key in ("suggestions", "goals", "items", "results"):
            if key in parsed and isinstance(parsed[key], list):
                return parsed[key]
        return []
    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")
        return []


def _get_weak_domains(user_id: str, db: Session, threshold: float = 50.0) -> list:
    """Return list of (domain_id, score) for domains below threshold, sorted ascending."""
    from app.models.domain_models import DomainGoal

    results = []
    for domain_id in DOMAIN_ORDER:
        goals = db.query(DomainGoal).filter_by(user_id=user_id, domain_id=domain_id, status="active").all()
        score = round(sum(g.progress for g in goals) / len(goals), 1) if goals else 0.0
        results.append((domain_id, score))

    # Sort by score ascending, return those below threshold
    results.sort(key=lambda x: x[1])
    weak = [(d, s) for d, s in results if s < threshold]

    # Always return at least 2 (the two weakest)
    return weak[:2] if len(weak) >= 2 else results[:2]


async def _generate_for_user(user_id: str, user_name: str, db: Session, notify: bool = True):
    """Generate AI suggestions for the 2 weakest domains and optionally push-notify."""
    from app.models.domain_models import DomainGoal

    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — suggestions skipped")
        return []

    weak_domains = _get_weak_domains(user_id, db)
    all_suggestions = []

    for domain_id, score in weak_domains:
        # Get existing goal titles to avoid duplicates
        existing = db.query(DomainGoal.title).filter_by(user_id=user_id, domain_id=domain_id).all()
        existing_titles = [r[0] for r in existing]

        # Delete stale suggestions for this domain
        db.query(GoalSuggestion).filter_by(user_id=user_id, domain_id=domain_id).delete()
        db.commit()

        prompt   = _build_prompt(domain_id, score, existing_titles, user_name)
        raw_sugs = _call_openai(prompt)

        expires = datetime.utcnow() + timedelta(days=7)
        for sug in raw_sugs[:3]:
            row = GoalSuggestion(
                id=str(_uuid.uuid4()),
                user_id=user_id,
                domain_id=domain_id,
                title=sug.get("title", "")[:255],
                description=sug.get("description", ""),
                category=sug.get("category", ""),
                why=sug.get("why", ""),
                difficulty=sug.get("difficulty", "medium"),
                domain_score=score,
                generated_at=datetime.utcnow(),
                expires_at=expires,
            )
            db.add(row)
            all_suggestions.append(row.to_dict())

    db.commit()

    # Push notify if user has subscriptions
    if notify and all_suggestions:
        weak_names = [DOMAIN_EMOJIS.get(d, '') + ' ' + d.title() for d, _ in weak_domains]
        send_push_to_user(user_id, {
            "title": "🎯 New Goal Ideas For You",
            "body":  f"We spotted some room to grow in {' & '.join(weak_names)}. Tap to see personalized suggestions.",
            "url":   "/domains?tab=suggestions",
            "tag":   "goal-suggestions",
            "actions": [
                {"action": "view", "title": "See Suggestions"},
                {"action": "dismiss", "title": "Later"},
            ],
        }, db)

    return all_suggestions


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("")
async def get_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return cached suggestions for the current user. Fresh if generated in last 7 days."""
    uid  = str(current_user.id)
    now  = datetime.utcnow()
    subs = (
        db.query(GoalSuggestion)
        .filter(
            GoalSuggestion.user_id == uid,
            (GoalSuggestion.expires_at == None) | (GoalSuggestion.expires_at > now),
            GoalSuggestion.accepted == None,  # hide already-acted-on ones
        )
        .order_by(GoalSuggestion.domain_id, GoalSuggestion.difficulty)
        .all()
    )
    # Group by domain
    grouped = {}
    for s in subs:
        grouped.setdefault(s.domain_id, []).append(s.to_dict())
    return {"suggestions": grouped, "count": len(subs)}


@router.post("/generate")
async def generate_suggestions(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger AI generation for the current user. Runs in background, returns immediately."""
    uid  = str(current_user.id)
    name = getattr(current_user, 'full_name', '') or getattr(current_user, 'email', 'user')
    background_tasks.add_task(_generate_for_user, uid, name, db, notify=False)
    return {"status": "generating", "message": "Suggestions will be ready in a few seconds."}


@router.post("/generate-all")
async def generate_all_suggestions(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Admin / cron endpoint — generates suggestions for all users with push subscriptions.
    Secure this with a cron secret header in production.
    """
    from app.api.push import PushSubscription
    user_ids = db.query(PushSubscription.user_id).distinct().all()
    user_ids = [r[0] for r in user_ids]

    async def run_all():
        for uid in user_ids:
            user = db.query(User).filter_by(id=uid).first()
            name = getattr(user, 'full_name', '') or getattr(user, 'email', 'user') if user else 'user'
            await _generate_for_user(uid, name, db, notify=True)

    background_tasks.add_task(run_all)
    return {"status": "started", "users": len(user_ids)}


@router.post("/{suggestion_id}/accept")
async def accept_suggestion(
    suggestion_id: str,
    body: AcceptSuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a suggestion → auto-creates a goal. Reject → hides it."""
    sug = db.query(GoalSuggestion).filter_by(id=suggestion_id, user_id=str(current_user.id)).first()
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    sug.accepted = str(body.accepted).lower()
    db.commit()

    if body.accepted:
        # Auto-create the goal
        from app.models.domain_models import DomainGoal
        import uuid as _u
        goal = DomainGoal(
            id=str(_u.uuid4()),
            user_id=str(current_user.id),
            domain_id=sug.domain_id,
            title=sug.title,
            description=sug.description,
            category=sug.category,
            progress=0,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return {"status": "accepted", "goal": goal.to_dict()}

    return {"status": "dismissed"}
