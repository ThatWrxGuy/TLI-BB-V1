# Busy Bee — Upgrade Package v5
**Branch**: `add-busy-bee-package-v1.4`

---

## What's in this package

| File | Destination | Feature |
|------|-------------|---------|
| `Goals.jsx`            | `frontend/src/pages/Goals.jsx`          | Detail drawer, confetti, sparklines |
| `Domains.jsx`          | `frontend/src/pages/Domains.jsx`        | Radar chart + **Suggestions tab** |
| `Dashboard.jsx`        | `frontend/src/pages/Dashboard.jsx`      | Domain scores widget |
| `SuggestionsPanel.jsx` | `frontend/src/components/SuggestionsPanel.jsx` | AI suggestions UI + Push toggle |
| `push_notifications.js`| `frontend/src/services/push.js`         | Web Push subscribe/unsubscribe |
| `sw.js`                | `public/sw.js`                          | Service worker for push |
| `push_backend.py`      | `app/api/push.py`                       | Push subscription + nightly reminder |
| `ai_suggestions.py`    | `app/api/ai_suggestions.py`             | GPT-4o-mini suggestions engine |
| `domains_db_patch.py`  | `app/api/domains.py`                    | DB-backed domains (Phase 2) |
| `db_models.py`         | `app/models/domain_models.py`           | All domain DB models |
| `alembic_migration.py` | `alembic/versions/bb_domains_v1.py`     | DB migration |
| `api_additions.js`     | replace `domainsAPI` in `api.js`        | All API methods incl. suggestions + push |

---

## Quick Install (new files only)

```bash
# Frontend
cp SuggestionsPanel.jsx  frontend/src/components/SuggestionsPanel.jsx
cp push_notifications.js frontend/src/services/push.js
cp sw.js                 public/sw.js

# Backend
cp push_backend.py    app/api/push.py
cp ai_suggestions.py  app/api/ai_suggestions.py
```

---

## Backend wiring

### 1. Register routers in `app/api/main.py`
```python
from app.api import push, ai_suggestions

app.include_router(push.router,            prefix="/api")
app.include_router(ai_suggestions.router,  prefix="/api")
```

### 2. Install deps
```bash
pip install pywebpush openai
```

### 3. Generate VAPID keys
```bash
npx web-push generate-vapid-keys
# OR
python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print('Private:', v.private_key.decode()); print('Public:', v.public_key.decode())"
```

### 4. Add to `.env`
```
VAPID_PRIVATE_KEY=your_private_key_here
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_EMAIL=mailto:you@busybee.app
OPENAI_API_KEY=sk-...
OPENAI_SUGGESTION_MODEL=gpt-4o-mini
```

### 5. Add to `frontend/.env`
```
VITE_VAPID_PUBLIC_KEY=your_public_key_here
```

### 6. Register service worker in `frontend/src/main.jsx`
```js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}
```

### 7. Add Suggestions tab to `Domains.jsx`
The tab is already in `Domains.jsx`. You also need to import `SuggestionsPanel`:
```js
import { SuggestionsPanel } from '../components/SuggestionsPanel'
```
It's already referenced in the file — just make sure the import path is correct.

### 8. Add Push Toggle to Settings page
```js
import { PushToggle } from '../components/SuggestionsPanel'
// then in your Settings JSX:
<PushToggle />
```

---

## DB migration additions

Add these two tables to your next Alembic migration
(snippets are at the top of `push_backend.py` and `ai_suggestions.py`):
- `push_subscriptions`
- `goal_suggestions`

---

## Cron jobs

### Nightly check-in reminder (8 PM)
```
0 20 * * * curl -s -X POST http://localhost:8000/api/push/remind-checkins \
  -H "X-Cron-Secret: $CRON_SECRET"
```

### Weekly AI suggestions (Sunday 9 AM)
```
0 9 * * 0 curl -s -X POST http://localhost:8000/api/suggestions/generate-all \
  -H "X-Cron-Secret: $CRON_SECRET"
```

Secure both endpoints by adding this check at the top:
```python
from fastapi import Request
if request.headers.get("X-Cron-Secret") != os.getenv("CRON_SECRET"):
    raise HTTPException(status_code=403)
```

---

## How it works end-to-end

```
User opens app
  → sw.js registers service worker
  → PushToggle in Settings → user flips switch
  → subscribeToPush() → browser asks permission → PushManager.subscribe()
  → POST /api/push/subscribe → stored in push_subscriptions table

Every Sunday 9 AM (cron)
  → POST /api/suggestions/generate-all
  → For each user with push sub:
      → find 2 weakest domains (lowest avg goal progress)
      → call GPT-4o-mini with domain context + existing goals
      → parse 3 suggestions per domain → store in goal_suggestions
      → send push: "🎯 New Goal Ideas For You"
      → user taps → /domains?tab=suggestions

Every night 8 PM (cron)
  → POST /api/push/remind-checkins
  → For each user with push sub who hasn't checked in today:
      → send push with "✅ Check In Now" action button
      → tap action → opens /domains directly

User sees suggestion
  → taps "Add Goal" → POST /api/suggestions/{id}/accept
  → auto-creates DomainGoal, marks suggestion accepted
  → disappears from suggestions list
```

---

## Next steps
- Radar share card (export SVG → PNG)
- Streak milestone pushes (7 / 30 / 100 days)
- Weekly progress digest (summary push, not email)
