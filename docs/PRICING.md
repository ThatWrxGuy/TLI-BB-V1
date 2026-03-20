# Busy Bee - Subscription Tiers

## Overview

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **Price** | $0 | $29/mo | $99/mo |
| **Email** | ✅ | ✅ | ✅ |
| **OAuth Login** | ✅ | ✅ | ✅ |
| **Demo Mode** | ✅ | ✅ | ✅ |
| **User Dashboard** | ✅ | ✅ | ✅ |
| **Goals** | 3 | Unlimited | Unlimited |
| **Tasks** | 10/mo | Unlimited | Unlimited |
| **Recommendations** | 5/mo | Unlimited | Unlimited |
| **Mood Tracking** | ✅ | ✅ | ✅ |
| **Calendar** | Basic | Advanced | Full |
| **Charts/Analytics** | Basic | Advanced | Full |
| **Domain Scores** | ✅ | ✅ | ✅ |
| **Plaid Finance** | ❌ | ✅ | ✅ |
| **Spending Insights** | ❌ | ✅ | ✅ |
| **Net Worth** | ❌ | ✅ | ✅ |
| **AI Chat** | 10/mo | Unlimited | Unlimited |
| **Executive Briefs** | 1/mo | Unlimited | Unlimited |
| **2FA** | ✅ | ✅ | ✅ |
| **Push Notifications** | ❌ | ✅ | ✅ |
| **Data Export** | ❌ | ✅ | ✅ |
| **API Access** | ❌ | ✅ | ✅ |
| **Custom Integrations** | ❌ | ❌ | ✅ |
| **Dedicated Support** | ❌ | ❌ | ✅ |
| **SLA** | ❌ | ❌ | ✅ |
| **White-label** | ❌ | ❌ | ✅ |
| **Admin Panel** | ❌ | ❌ | ✅ |
| **User Management** | ❌ | ❌ | ✅ |
| **Webhooks** | ❌ | ❌ | ✅ |

---

## Feature Details

### 🔓 Free Tier ($0)

Perfect for trying out the platform.

- **Authentication**
  - Email/password signup & login
  - OAuth (GitHub, Google)
  - Email verification
  - Demo mode
  - Password reset

- **Core Features**
  - User dashboard with overview
  - Up to 3 goals
  - Up to 10 tasks/month
  - 5 AI recommendations/month
  - Basic calendar view
  - Basic charts
  - Mood tracking
  - Domain scores

- **Security**
  - 2FA (optional)
  - Session management
  - Password change

---

### 💎 Pro Tier ($29/mo)

For individuals who want full access.

**Everything in Free, plus:**

- **Unlimited Features**
  - Unlimited goals
  - Unlimited tasks
  - Unlimited AI recommendations
  - Unlimited AI chat
  - Unlimited executive briefs

- **Finance (Plaid)**
  - Connect bank accounts
  - Transaction history
  - Spending insights
  - Net worth tracking
  - Monthly spending analytics

- **Enhanced Experience**
  - Advanced calendar
  - Advanced analytics
  - Push notifications
  - Data export (JSON/CSV)

- **API Access**
  - REST API access
  - Custom integrations

---

### 🏢 Enterprise Tier ($99/mo)

For teams and organizations.

**Everything in Pro, plus:**

- **Team Features**
  - Admin panel
  - User management
  - Role management
  - Team analytics

- **Advanced**
  - Custom integrations
  - Webhooks
  - White-label options

- **Support**
  - Dedicated account manager
  - Priority support
  - Custom SLAs
  - On-premise deployment option

---

## API Endpoints by Tier

### Public (No Auth)
- `POST /auth/signup` - Sign up
- `POST /auth/login` - Login
- `GET /auth/oauth/{provider}` - OAuth
- `POST /auth/verify` - Verify email
- `POST /auth/password-reset-request` - Reset password
- `GET /demo/start` - Start demo
- `GET /health` - Health check

### Free & Above
- `GET /dashboard` - Dashboard
- `GET /dashboard/overview` - Stats
- `GET /dashboard/goals` - Goals
- `POST /dashboard/goals` - Create goal
- `GET /dashboard/tasks` - Tasks
- `POST /dashboard/tasks` - Create task
- `PATCH /dashboard/tasks/{id}/toggle` - Toggle task
- `GET /dashboard/recommendations` - AI Recs
- `GET /dashboard/domain-scores` - Scores
- `GET /dashboard/mood` - Mood
- `POST /dashboard/mood` - Log mood
- `GET /dashboard/charts` - Charts
- `GET /dashboard/calendar` - Calendar
- `GET /dashboard/quick-actions` - Actions
- `GET /onboarding/status` - Onboarding
- `POST /onboarding/*` - Complete onboarding
- `GET /profile` - Profile
- `PATCH /profile` - Update profile
- `GET /profile/settings` - Settings
- `POST /profile/password` - Change password
- `GET /profile/two-factor/status` - 2FA status
- `POST /profile/two-factor/*` - 2FA setup/disable

### Pro & Above
- `GET /finance/accounts` - Linked accounts
- `POST /finance/plaid/link` - Link bank
- `GET /finance/transactions` - Transactions
- `GET /finance/insights` - Spending insights
- `GET /finance/net-worth` - Net worth
- `GET /finance/monthly` - Monthly history
- `GET /notifications/push-tokens` - Push tokens
- `POST /notifications/send` - Send push
- `GET /profile/export` - Export data

### Enterprise Only
- `GET /admin/stats` - Platform stats
- `GET /admin/users` - All users
- `GET /admin/metrics/*` - Revenue metrics
- `GET /admin/transactions` - All transactions
- `GET /admin/health` - System health
- `GET /admin/features/usage` - Usage
- `GET /admin/webhooks` - Webhooks
- `POST /admin/webhooks` - Create webhook
- `GET /admin/analytics` - Platform analytics

---

## Implementation Notes

### Tier Enforcement
In production, check user subscription tier in middleware:

```python
def require_pro(require_verified_email: bool = True):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.subscription_tier == SubscriptionTier.FREE:
            raise HTTPException(403, "Upgrade to Pro for this feature")
        return current_user
    return checker
```

### Rate Limits
- **Free**: 100 requests/day
- **Pro**: 10,000 requests/day
- **Enterprise**: Unlimited

### Storage
- **Free**: 100MB
- **Pro**: 10GB
- **Enterprise**: Unlimited
