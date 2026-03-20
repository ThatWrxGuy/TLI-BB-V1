# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Billing API routes with Stripe integration."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import secrets

from app.models.user import User, UserRole, SubscriptionTier
from app.api.auth import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing"])

# In-memory storage (replace with database in production)
subscriptions_db: dict[str, dict] = {}

# Stripe configuration (should be in environment variables)
STRIPE_SECRET_KEY = "sk_test_your_key"
STRIPE_PUBLISHABLE_KEY = "pk_test_your_key"
STRIPE_WEBHOOK_SECRET = "whsec_your_secret"

# Pricing configuration
PRICES = {
    "pro": {
        "monthly": "price_pro_monthly",
        "yearly": "price_pro_yearly"
    },
    "enterprise": {
        "monthly": "price_enterprise_monthly",
        "yearly": "price_enterprise_yearly"
    }
}


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateCheckoutRequest(BaseModel):
    """Create checkout session request."""
    price_id: str
    success_url: str = "http://localhost:3000/dashboard?success=true"
    cancel_url: str = "http://localhost:3000/pricing?canceled=true"


class CheckoutResponse(BaseModel):
    """Checkout session response."""
    checkout_url: str
    session_id: str


class PortalResponse(BaseModel):
    """Customer portal response."""
    portal_url: str


class SubscriptionResponse(BaseModel):
    """Subscription details response."""
    subscription_id: str
    tier: str
    status: str
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False


class WebhookEvent(BaseModel):
    """Stripe webhook event."""
    type: str
    data: dict


# ==================== HELPER FUNCTIONS ====================

def get_stripe_customer(user: User) -> str:
    """Get or create Stripe customer for user."""
    return user.stripe_customer_id or f"cus_{secrets.token_urlsafe(16)}"


def create_stripe_checkout(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str
) -> tuple[str, str]:
    """Create a Stripe checkout session.
    
    Returns: (checkout_url, session_id)
    """
    # TODO: Use actual Stripe SDK
    # import stripe
    # stripe.api_key = STRIPE_SECRET_KEY
    # session = stripe.checkout.Session.create(
    #     customer=customer_id,
    #     payment_method_types=['card'],
    #     line_items=[{'price': price_id, 'quantity': 1}],
    #     mode='subscription',
    #     success_url=success_url,
    #     cancel_url=cancel_url
    # )
    # return session.url, session.id
    
    # Placeholder response
    session_id = f"cs_{secrets.token_urlsafe(24)}"
    checkout_url = f"https://checkout.stripe.com/pay/{session_id}"
    
    return checkout_url, session_id


def create_stripe_portal(customer_id: str) -> str:
    """Create Stripe customer portal session."""
    # TODO: Use actual Stripe SDK
    # import stripe
    # stripe.api_key = STRIPE_SECRET_KEY
    # session = stripe.billing_portal.Session.create(
    #     customer=customer_id,
    #     return_url="http://localhost:3000/dashboard"
    # )
    # return session.url
    
    # Placeholder response
    return f"https://billing.stripe.com/session/{secrets.token_urlsafe(16)}"


def cancel_stripe_subscription(subscription_id: str) -> dict:
    """Cancel Stripe subscription."""
    # TODO: Use actual Stripe SDK
    # import stripe
    # stripe.api_key = STRIPE_SECRET_KEY
    # subscription = stripe.Subscription.modify(
    #     subscription_id,
    #     cancel_at_period_end=True
    # )
    # return subscription
    
    return {
        "id": subscription_id,
        "status": "active",
        "cancel_at_period_end": True
    }


# ==================== BILLING ROUTES ====================

@router.get("/prices")
async def get_prices():
    """Get available subscription prices."""
    return {
        "prices": {
            "pro": {
                "monthly": {
                    "id": "price_pro_monthly",
                    "amount": 2900,  # $29.00
                    "currency": "usd",
                    "interval": "month"
                },
                "yearly": {
                    "id": "price_pro_yearly",
                    "amount": 29000,  # $290.00
                    "currency": "usd",
                    "interval": "year"
                }
            },
            "enterprise": {
                "monthly": {
                    "id": "price_enterprise_monthly",
                    "amount": 9900,  # $99.00
                    "currency": "usd",
                    "interval": "month"
                },
                "yearly": {
                    "id": "price_enterprise_yearly",
                    "amount": 99000,  # $990.00
                    "currency": "usd",
                    "interval": "year"
                }
            }
        }
    }


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription."""
    
    valid_price_ids = [
        "price_pro_monthly", "price_pro_yearly",
        "price_enterprise_monthly", "price_enterprise_yearly"
    ]
    
    if request.price_id not in valid_price_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid price_id. Valid: {valid_price_ids}"
        )
    
    # Get or create Stripe customer
    customer_id = get_stripe_customer(current_user)
    
    # Create checkout session
    checkout_url, session_id = create_stripe_checkout(
        customer_id=customer_id,
        price_id=request.price_id,
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )
    
    # Store pending subscription
    subscriptions_db[session_id] = {
        "user_id": current_user.id,
        "price_id": request.price_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    return CheckoutResponse(
        checkout_url=checkout_url,
        session_id=session_id
    )


@router.get("/portal", response_model=PortalResponse)
async def get_customer_portal(current_user: User = Depends(get_current_user)):
    """Get Stripe customer portal URL."""
    
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    portal_url = create_stripe_portal(current_user.stripe_customer_id)
    
    return PortalResponse(portal_url=portal_url)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: User = Depends(get_current_user)):
    """Get current subscription details."""
    
    if not current_user.stripe_subscription_id:
        return SubscriptionResponse(
            subscription_id="",
            tier=current_user.subscription_tier.value,
            status="free",
            current_period_start=None,
            current_period_end=None,
            cancel_at_period_end=False
        )
    
    # TODO: Fetch from Stripe
    return SubscriptionResponse(
        subscription_id=current_user.stripe_subscription_id or "",
        tier=current_user.subscription_tier.value,
        status="active",
        current_period_start=datetime.utcnow().isoformat(),
        current_period_end=(datetime.utcnow() + __import__('datetime').timedelta(days=30)).isoformat(),
        cancel_at_period_end=False
    )


@router.post("/subscription/cancel")
async def cancel_subscription(current_user: User = Depends(get_current_user)):
    """Cancel subscription at period end."""
    
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription to cancel"
        )
    
    result = cancel_stripe_subscription(current_user.stripe_subscription_id)
    
    return {
        "message": "Subscription will be canceled at the end of the billing period",
        "subscription": result
    }


@router.post("/subscription/reactivate")
async def reactivate_subscription(current_user: User = Depends(get_current_user)):
    """Reactivate a canceled subscription."""
    
    # TODO: Use Stripe API to reactivate
    
    return {
        "message": "Subscription reactivated successfully"
    }


@router.post("/webhook")
async def stripe_webhook(payload: bytes, signature: str):
    """Handle Stripe webhooks."""
    
    # TODO: Verify webhook signature
    # TODO: Handle events:
    # - checkout.session.completed
    # - customer.subscription.created
    # - customer.subscription.updated
    # - customer.subscription.deleted
    # - invoice.payment_succeeded
    # - invoice.payment_failed
    
    # Verify signature
    # import stripe
    # stripe.api_key = STRIPE_SECRET_KEY
    # event = stripe.Webhook.construct_event(
    #     payload, signature, STRIPE_WEBHOOK_SECRET
    # )
    
    # For now, acknowledge receipt
    return {"received": True}


# ==================== ADMIN ROUTES ====================

@router.get("/admin/subscriptions", response_model=list[SubscriptionResponse])
async def list_all_subscriptions(
    current_user: User = Depends(get_current_user)
):
    """List all subscriptions (admin only)."""
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # TODO: Return all subscriptions from database
    
    return []


@router.post("/admin/subscription/{user_id}/update")
async def admin_update_subscription(
    user_id: str,
    tier: SubscriptionTier,
    current_user: User = Depends(get_current_user)
):
    """Update user subscription tier (admin)."""
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # TODO: Update user subscription in database
    
    return {
        "message": f"Subscription updated to {tier.value}",
        "user_id": user_id,
        "tier": tier.value
    }
