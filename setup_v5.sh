#!/usr/bin/env bash
# Busy Bee V5 — Final Setup Script
# Run from repo root: bash setup_v5.sh
# Does: deps, VAPID key gen, .env patching, SW registration, DB migration
# ─────────────────────────────────────────────────────────────────────────────

set -e

BOLD="\033[1m"; GREEN="\033[32m"; YELLOW="\033[33m"; CYAN="\033[36m"; RED="\033[31m"; RESET="\033[0m"

echo -e "\n${BOLD}${CYAN}🐝 Busy Bee V5 — Final Setup${RESET}\n"

# ── Sanity check ──────────────────────────────────────────────────────────────
if [ ! -d "frontend" ] || [ ! -d "app" ]; then
  echo -e "${RED}Run from repo root (contains frontend/ and app/).${RESET}"; exit 1
fi

# ── 1. Python deps ────────────────────────────────────────────────────────────
echo -e "${BOLD}[1/5] Installing Python dependencies…${RESET}"
pip install pywebpush openai py-vapid --quiet
echo -e "  ${GREEN}✓${RESET} pywebpush, openai, py-vapid installed"

# ── 2. Generate VAPID keys ────────────────────────────────────────────────────
echo -e "\n${BOLD}[2/5] Generating VAPID keys…${RESET}"
VAPID_OUTPUT=$(python3 - <<'PYEOF'
from py_vapid import Vapid
import base64, struct, json
v = Vapid()
v.generate_keys()
private = v.private_key.private_bytes(
    encoding=__import__('cryptography').hazmat.primitives.serialization.Encoding.PEM,
    format=__import__('cryptography').hazmat.primitives.serialization.PrivateFormat.PKCS8,
    encryption_algorithm=__import__('cryptography').hazmat.primitives.serialization.NoEncryption()
).decode().strip()
public = v.public_key.public_bytes(
    encoding=__import__('cryptography').hazmat.primitives.serialization.Encoding.X962,
    format=__import__('cryptography').hazmat.primitives.serialization.PublicFormat.UncompressedPoint
)
pub_b64 = base64.urlsafe_b64encode(public).rstrip(b'=').decode()
# private key as base64 for pywebpush
priv_der = v.private_key.private_bytes(
    encoding=__import__('cryptography').hazmat.primitives.serialization.Encoding.DER,
    format=__import__('cryptography').hazmat.primitives.serialization.PrivateFormat.PKCS8,
    encryption_algorithm=__import__('cryptography').hazmat.primitives.serialization.NoEncryption()
)
priv_b64 = base64.urlsafe_b64encode(priv_der).rstrip(b'=').decode()
print(f"PRIVATE={priv_b64}")
print(f"PUBLIC={pub_b64}")
PYEOF
)

VAPID_PRIVATE=$(echo "$VAPID_OUTPUT" | grep PRIVATE | cut -d= -f2-)
VAPID_PUBLIC=$(echo "$VAPID_OUTPUT"  | grep PUBLIC  | cut -d= -f2-)

echo -e "  ${GREEN}✓${RESET} VAPID keys generated"

# ── 3. Patch .env files ───────────────────────────────────────────────────────
echo -e "\n${BOLD}[3/5] Writing env vars…${RESET}"

BACKEND_ENV=".env"
FRONTEND_ENV="frontend/.env"

# Helper: set or replace a var in an env file
set_env() {
  local file="$1" key="$2" value="$3"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
    echo -e "  ${YELLOW}↻${RESET}  Updated ${key} in ${file}"
  else
    echo "${key}=${value}" >> "$file"
    echo -e "  ${GREEN}+${RESET}  Added ${key} to ${file}"
  fi
}

touch "$BACKEND_ENV" "$FRONTEND_ENV"

set_env "$BACKEND_ENV" "VAPID_PRIVATE_KEY" "$VAPID_PRIVATE"
set_env "$BACKEND_ENV" "VAPID_PUBLIC_KEY"  "$VAPID_PUBLIC"
set_env "$BACKEND_ENV" "VAPID_EMAIL"       "mailto:admin@busybee.app"

# Generate a random CRON_SECRET if not already set
if ! grep -q "^CRON_SECRET=" "$BACKEND_ENV" 2>/dev/null; then
  CRON_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
  set_env "$BACKEND_ENV" "CRON_SECRET" "$CRON_SECRET"
fi

# OpenAI key — prompt if not already set
if ! grep -q "^OPENAI_API_KEY=sk-" "$BACKEND_ENV" 2>/dev/null; then
  echo ""
  read -p "  Enter your OpenAI API key (sk-...): " OPENAI_KEY
  if [ -n "$OPENAI_KEY" ]; then
    set_env "$BACKEND_ENV" "OPENAI_API_KEY" "$OPENAI_KEY"
    set_env "$BACKEND_ENV" "OPENAI_SUGGESTION_MODEL" "gpt-4o-mini"
  else
    echo -e "  ${YELLOW}⚠️  Skipped. Add OPENAI_API_KEY manually to .env before using suggestions.${RESET}"
  fi
fi

set_env "$FRONTEND_ENV" "VITE_VAPID_PUBLIC_KEY" "$VAPID_PUBLIC"

echo -e "  ${GREEN}✓${RESET} .env and frontend/.env updated"

# ── 4. Service worker registration in main.jsx ────────────────────────────────
echo -e "\n${BOLD}[4/5] Registering service worker in main.jsx…${RESET}"

MAIN_JSX="frontend/src/main.jsx"
if [ -f "$MAIN_JSX" ]; then
  if grep -q "serviceWorker" "$MAIN_JSX"; then
    echo -e "  ${YELLOW}ℹ${RESET}  Service worker already registered in main.jsx"
  else
    cp "$MAIN_JSX" "${MAIN_JSX}.bak"
    # Append SW registration before closing of file
    cat >> "$MAIN_JSX" << 'SWEOF'

// ── Push notification service worker ──────────────────────────────────────────
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(err => {
      console.warn('SW registration failed:', err)
    })
  })
}
SWEOF
    echo -e "  ${GREEN}✓${RESET} Service worker registration added to main.jsx"
  fi
else
  echo -e "  ${YELLOW}⚠️  main.jsx not found at ${MAIN_JSX}. Add SW registration manually:${RESET}"
  echo -e "     if ('serviceWorker' in navigator) { navigator.serviceWorker.register('/sw.js') }"
fi

# ── 5. Alembic migration for new tables ───────────────────────────────────────
echo -e "\n${BOLD}[5/5] Database migration (push_subscriptions + goal_suggestions)…${RESET}"

if command -v alembic &>/dev/null && [ -d "alembic/versions" ]; then
  CURRENT_HEAD=$(alembic heads 2>/dev/null | awk '{print $1}' | head -1)
  MIGRATION_FILE="alembic/versions/bb_push_suggestions_v5.py"

  cat > "$MIGRATION_FILE" << MIGEOF
"""Busy Bee V5 — push_subscriptions + goal_suggestions tables

Revision ID: bb_v5_push_suggestions
Revises: ${CURRENT_HEAD}
Create Date: $(date -u +"%Y-%m-%d %H:%M:%S.000000")
"""
from alembic import op
import sqlalchemy as sa

revision = 'bb_v5_push_suggestions'
down_revision = '${CURRENT_HEAD}'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'push_subscriptions',
        sa.Column('id',         sa.String(36),  primary_key=True),
        sa.Column('user_id',    sa.String(36),  nullable=False),
        sa.Column('endpoint',   sa.Text(),      nullable=False, unique=True),
        sa.Column('p256dh',     sa.Text(),      nullable=False),
        sa.Column('auth',       sa.Text(),      nullable=False),
        sa.Column('created_at', sa.DateTime(),  server_default=sa.func.now()),
        sa.Column('last_used',  sa.DateTime(),  nullable=True),
    )
    op.create_index('ix_push_subs_user_id', 'push_subscriptions', ['user_id'])

    op.create_table(
        'goal_suggestions',
        sa.Column('id',           sa.String(36),  primary_key=True),
        sa.Column('user_id',      sa.String(36),  nullable=False),
        sa.Column('domain_id',    sa.String(32),  nullable=False),
        sa.Column('title',        sa.String(255), nullable=False),
        sa.Column('description',  sa.Text(),      nullable=True),
        sa.Column('category',     sa.String(64),  nullable=True),
        sa.Column('why',          sa.Text(),      nullable=True),
        sa.Column('difficulty',   sa.String(16),  nullable=True),
        sa.Column('domain_score', sa.Float(),     nullable=True),
        sa.Column('accepted',     sa.String(5),   nullable=True),
        sa.Column('generated_at', sa.DateTime(),  server_default=sa.func.now()),
        sa.Column('expires_at',   sa.DateTime(),  nullable=True),
    )
    op.create_index('ix_suggestions_user_id',   'goal_suggestions', ['user_id'])
    op.create_index('ix_suggestions_domain_id', 'goal_suggestions', ['domain_id'])

def downgrade():
    op.drop_table('goal_suggestions')
    op.drop_table('push_subscriptions')
MIGEOF

  echo -e "  ${GREEN}✓${RESET} Migration written → ${MIGRATION_FILE}"
  echo -e "\n  Applying migration…"
  alembic upgrade head && echo -e "  ${GREEN}✓${RESET} Migration applied!" || echo -e "  ${YELLOW}⚠️  Run manually: alembic upgrade head${RESET}"
else
  echo -e "  ${YELLOW}ℹ${RESET}  Alembic not found or no versions/ dir. Migration SQL:"
  echo -e "     CREATE TABLE push_subscriptions (id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36), endpoint TEXT UNIQUE, p256dh TEXT, auth TEXT, created_at DATETIME, last_used DATETIME);"
  echo -e "     CREATE TABLE goal_suggestions (id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36), domain_id VARCHAR(32), title VARCHAR(255), description TEXT, category VARCHAR(64), why TEXT, difficulty VARCHAR(16), domain_score FLOAT, accepted VARCHAR(5), generated_at DATETIME, expires_at DATETIME);"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}${GREEN}✅ V5 setup complete!${RESET}\n"
CRON_SECRET_VAL=$(grep "^CRON_SECRET=" .env 2>/dev/null | cut -d= -f2-)
echo -e "${BOLD}Restart your server:${RESET}"
echo -e "  ${CYAN}uvicorn app.api.main:app --reload${RESET}"
echo -e "  ${CYAN}cd frontend && npm run dev${RESET}\n"
echo -e "${BOLD}Add these cron jobs:${RESET}"
echo -e "  ${CYAN}# Nightly check-in reminder (8 PM)"
echo -e "  0 20 * * * curl -s -X POST http://localhost:8000/api/push/remind-checkins -H 'X-Cron-Secret: ${CRON_SECRET_VAL}'"
echo -e ""
echo -e "  # Weekly AI suggestions (Sunday 9 AM)"
echo -e "  0 9 * * 0  curl -s -X POST http://localhost:8000/api/suggestions/generate-all -H 'X-Cron-Secret: ${CRON_SECRET_VAL}'${RESET}\n"
echo -e "${BOLD}Test push:${RESET}"
echo -e "  Log in → Settings → flip the notification toggle → you should get a welcome push.\n"
