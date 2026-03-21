# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Plaid integration for financial data."""

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

router = APIRouter(prefix="/finance", tags=["Finance - Plaid"])

# In-memory storage (replace with database)
linked_accounts_db: dict[str, list[dict]] = {}
transactions_db: dict[str, list[dict]] = {}
holdings_db: dict[str, list[dict]] = {}


# ==================== ENUMS ====================

class AccountType(str, Enum):
    """Bank account types."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"


class TransactionCategory(str, Enum):
    """Transaction categories."""
    FOOD = "food"
    TRANSPORTATION = "transportation"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    BILLS = "bills"
    INCOME = "income"
    TRANSFER = "transfer"
    OTHER = "other"


# ==================== RESPONSE MODELS ====================

class LinkedAccount(BaseModel):
    """Linked bank account."""
    id: str
    institution_name: str
    institution_logo: Optional[str] = None
    account_name: str
    account_type: str
    account_mask: str  # Last 4 digits
    current_balance: float
    available_balance: Optional[float] = None
    currency: str = "USD"
    is_connected: bool = True
    last_synced: str


class LinkedAccountsResponse(BaseModel):
    """Linked accounts response."""
    accounts: List[LinkedAccount]
    total_balance: float
    accounts_count: int


class Transaction(BaseModel):
    """Financial transaction."""
    id: str
    account_id: str
    date: str
    name: str
    merchant_name: Optional[str] = None
    amount: float  # Negative = spending, Positive = income
    category: str
    is_pending: bool = False
    logo_url: Optional[str] = None


class TransactionsResponse(BaseModel):
    """Transactions response."""
    transactions: List[Transaction]
    total_transactions: int
    total_spending: float
    total_income: float


class SpendingByCategory(BaseModel):
    """Spending breakdown by category."""
    category: str
    amount: float
    percentage: float
    icon: str


class SpendingInsights(BaseModel):
    """Spending insights."""
    total_spending: float
    total_income: float
    net_flow: float
    spending_by_category: List[SpendingByCategory]
    average_daily_spending: float
    top_merchants: List[dict]
    month_over_month_change: float  # percentage
    insights: List[str]


class MonthlySpending(BaseModel):
    """Monthly spending data."""
    month: str
    spending: float
    income: float


class NetWorth(BaseModel):
    """Net worth calculation."""
    total_assets: float
    total_liabilities: float
    net_worth: float
    change_30_days: float


# ==================== HELPER FUNCTIONS ====================

def generate_demo_transactions(account_id: str, num: int = 30) -> List[dict]:
    """Generate demo transactions."""
    
    categories = [
        {"category": "food", "icon": "🍔", "merchants": ["Whole Foods", "Trader Joe's", "Uber Eats", "Chipotle", "Starbucks"]},
        {"category": "transportation", "icon": "🚗", "merchants": ["Uber", "Lyft", "Shell", "Chevron", "Parking"]},
        {"category": "shopping", "icon": "🛒", "merchants": ["Amazon", "Target", "Walmart", "Best Buy", "Nike"]},
        {"category": "entertainment", "icon": "🎬", "merchants": ["Netflix", "Spotify", "AMC Theaters", "Steam", "Apple"]},
        {"category": "bills", "icon": "📄", "merchants": ["AT&T", "Comcast", "PG&E", "Water Company", "Insurance"]},
        {"category": "income", "icon": "💰", "merchants": ["Employer Direct Deposit", "Payroll", "Dividend", "Interest"]},
    ]
    
    transactions = []
    base_date = datetime.utcnow()
    
    for i in range(num):
        # 80% spending, 20% income
        if random.random() < 0.8:
            cat = random.choice([c for c in categories if c["category"] != "income"])
            amount = round(random.uniform(5, 200) * -1, 2)
        else:
            cat = random.choice([c for c in categories if c["category"] == "income"])
            amount = round(random.uniform(500, 5000), 2)
        
        merchant = random.choice(cat["merchants"])
        
        transactions.append({
            "id": str(uuid.uuid4()),
            "account_id": account_id,
            "date": (base_date - timedelta(days=i)).strftime("%Y-%m-%d"),
            "name": merchant,
            "merchant_name": merchant,
            "amount": amount,
            "category": cat["category"],
            "is_pending": i == 0 and random.random() < 0.3,
            "logo_url": None
        })
    
    return sorted(transactions, key=lambda x: x["date"], reverse=True)


# ==================== PLAID LINK FLOW ====================

class PlaidLinkTokenResponse(BaseModel):
    """Plaid link token response."""
    link_token: str
    expiration: str


class PlaidLinkSuccessResponse(BaseModel):
    """Plaid link success response."""
    public_token: str
    metadata: dict


@router.get("/plaid/link-token", response_model=PlaidLinkTokenResponse)
async def create_plaid_link_token(
    current_user: User = Depends(get_current_user)
):
    """Create Plaid Link token for connecting bank accounts."""
    
    # TODO: Use actual Plaid SDK
    # import plaid
    # client = PlaidApi(plaid_configuration)
    # response = client.link_token_create({
    #     'user': {'client_user_id': user_id},
    #     'client_name': 'Busy Bee',
    #     'products': ['transactions'],
    #     'country_codes': ['US'],
    #     'language': 'en'
    # })
    
    # Demo response
    link_token = f"link-sandbox-{uuid.uuid4()}"
    expiration = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    
    return PlaidLinkTokenResponse(
        link_token=link_token,
        expiration=expiration
    )


@router.post("/plaid/link")
async def link_account(
    public_token: str,
    current_user: User = Depends(get_current_user)
):
    """Exchange public token for access token and link account."""
    
    user_id = current_user.id
    
    # TODO: Use actual Plaid SDK to exchange token
    # import plaid
    # client = PlaidApi(plaid_configuration)
    # response = client.item_public_token_exchange({
    #     'public_token': public_token
    # })
    # access_token = response['access_token']
    # item_id = response['item_id']
    
    # Demo: Create linked account
    institutions = [
        {"name": "Chase", "logo": "https://plaid.com/images/chase.png"},
        {"name": "Bank of America", "logo": "https://plaid.com/images/boa.png"},
        {"name": "Wells Fargo", "logo": "https://plaid.com/images/wells.png"},
        {"name": "Citi", "logo": "https://plaid.com/images/citi.png"},
    ]
    
    institution = random.choice(institutions)
    account_types = ["checking", "savings", "credit"]
    account_type = random.choice(account_types)
    
    account = {
        "id": str(uuid.uuid4()),
        "institution_name": institution["name"],
        "institution_logo": institution["logo"],
        "account_name": f"{institution['name']} {account_type.title()}",
        "account_type": account_type,
        "account_mask": str(random.randint(1000, 9999)),
        "current_balance": round(random.uniform(1000, 25000), 2),
        "available_balance": round(random.uniform(500, 20000), 2),
        "currency": "USD",
        "is_connected": True,
        "last_synced": datetime.utcnow().isoformat(),
        "access_token": f"access-{uuid.uuid4()}"
    }
    
    if user_id not in linked_accounts_db:
        linked_accounts_db[user_id] = []
    
    linked_accounts_db[user_id].append(account)
    
    # Generate transactions for this account
    transactions_db[account["id"]] = generate_demo_transactions(account["id"])
    
    return {
        "message": "Account linked successfully",
        "account": LinkedAccount(**{k: v for k, v in account.items() if k != "access_token"})
    }


@router.get("/accounts", response_model=LinkedAccountsResponse)
async def get_linked_accounts(
    current_user: User = Depends(get_current_user)
):
    """Get all linked bank accounts."""
    
    user_id = current_user.id
    
    # Generate demo accounts if none exist
    if user_id not in linked_accounts_db or not linked_accounts_db[user_id]:
        # Create demo account
        account = {
            "id": str(uuid.uuid4()),
            "institution_name": "Chase",
            "institution_logo": None,
            "account_name": "Chase Checking",
            "account_type": "checking",
            "account_mask": "4521",
            "current_balance": 12543.67,
            "available_balance": 12043.67,
            "currency": "USD",
            "is_connected": True,
            "last_synced": datetime.utcnow().isoformat()
        }
        
        linked_accounts_db[user_id] = [account]
        transactions_db[account["id"]] = generate_demo_transactions(account["id"])
    
    accounts = linked_accounts_db.get(user_id, [])
    total = sum(a["current_balance"] for a in accounts)
    
    return LinkedAccountsResponse(
        accounts=[LinkedAccount(**{k: v for k, v in a.items() if k != "access_token"}) for a in accounts],
        total_balance=round(total, 2),
        accounts_count=len(accounts)
    )


@router.post("/accounts/{account_id}/sync")
async def sync_account(
    account_id: str,
    current_user: User = Depends(get_current_user)
):
    """Sync account transactions."""
    
    user_id = current_id = current_user.id
    
    # TODO: Use Plaid to fetch new transactions
    # import plaid
    # client = PlaidApi(plaid_configuration)
    # response = client.transactions_sync({
    #     'access_token': access_token
    # })
    
    return {
        "message": "Account synced",
        "new_transactions": random.randint(0, 5)
    }


@router.get("/transactions", response_model=TransactionsResponse)
async def get_transactions(
    current_user: User = Depends(get_current_user),
    account_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Get transactions from linked accounts."""
    
    user_id = current_user.id
    
    if user_id not in linked_accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked accounts"
        )
    
    all_transactions = []
    for account in linked_accounts_db[user_id]:
        if account_id and account["id"] != account_id:
            continue
        if account["id"] in transactions_db:
            all_transactions.extend(transactions_db[account["id"]])
    
    # Filter by date
    if start_date:
        all_transactions = [t for t in all_transactions if t["date"] >= start_date]
    if end_date:
        all_transactions = [t for t in all_transactions if t["date"] <= end_date]
    
    # Filter by category
    if category:
        all_transactions = [t for t in all_transactions if t["category"] == category]
    
    # Sort by date
    all_transactions = sorted(all_transactions, key=lambda x: x["date"], reverse=True)
    
    # Limit
    all_transactions = all_transactions[:limit]
    
    total_spending = sum(abs(t["amount"]) for t in all_transactions if t["amount"] < 0)
    total_income = sum(t["amount"] for t in all_transactions if t["amount"] > 0)
    
    return TransactionsResponse(
        transactions=[Transaction(**t) for t in all_transactions],
        total_transactions=len(all_transactions),
        total_spending=round(total_spending, 2),
        total_income=round(total_income, 2)
    )


@router.get("/insights", response_model=SpendingInsights)
async def get_spending_insights(
    current_user: User = Depends(get_current_user),
    days: int = 30
):
    """Get spending insights and analytics."""
    
    user_id = current_user.id
    
    if user_id not in linked_accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked accounts"
        )
    
    # Get all transactions
    all_transactions = []
    for account in linked_accounts_db.get(user_id, []):
        all_transactions.extend(transactions_db.get(account["id"], []))
    
    # Get last N days
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [t for t in all_transactions if t["date"] >= cutoff]
    
    # Calculate spending by category
    spending_by_cat = {}
    for t in recent:
        if t["amount"] < 0:  # Spending only
            cat = t["category"]
            spending_by_cat[cat] = spending_by_cat.get(cat, 0) + abs(t["amount"])
    
    total_spending = sum(spending_by_cat.values())
    total_income = sum(t["amount"] for t in recent if t["amount"] > 0)
    
    categories_info = {
        "food": "🍔",
        "transportation": "🚗",
        "shopping": "🛒",
        "entertainment": "🎬",
        "bills": "📄",
        "other": "📦"
    }
    
    spending_by_category = [
        SpendingByCategory(
            category=cat,
            amount=round(amount, 2),
            percentage=round((amount / total_spending * 100), 1) if total_spending > 0 else 0,
            icon=categories_info.get(cat, "📦")
        )
        for cat, amount in sorted(spending_by_cat.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Top merchants
    merchant_spending = {}
    for t in recent:
        if t["amount"] < 0:
            m = t["merchant_name"] or t["name"]
            merchant_spending[m] = merchant_spending.get(m, 0) + abs(t["amount"])
    
    top_merchants = [
        {"name": m, "amount": round(a, 2)}
        for m, a in sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Average daily spending
    avg_daily = total_spending / days if days > 0 else 0
    
    # Generate insights
    insights = []
    if avg_daily > 100:
        insights.append("💡 Your daily spending is above average. Consider setting a budget.")
    if spending_by_cat.get("food", 0) > total_spending * 0.3:
        insights.append("🍔 Food expenses are high this month. Meal prep could help save money.")
    if spending_by_cat.get("shopping", 0) > total_spending * 0.2:
        insights.append("🛒 Shopping expenses are notable. Review unnecessary purchases?")
    
    if total_income > total_spending:
        insights.append("✅ Great job! You're saving more than you're spending.")
    
    insights.append(f"📊 You've spent ${total_spending:.2f} in the last {days} days.")
    
    return SpendingInsights(
        total_spending=round(total_spending, 2),
        total_income=round(total_income, 2),
        net_flow=round(total_income - total_spending, 2),
        spending_by_category=spending_by_category,
        average_daily_spending=round(avg_daily, 2),
        top_merchants=top_merchants,
        month_over_month_change=round(random.uniform(-15, 15), 1),
        insights=insights
    )


@router.get("/net-worth", response_model=NetWorth)
async def get_net_worth(
    current_user: User = Depends(get_current_user)
):
    """Calculate net worth."""
    
    user_id = current_user.id
    
    if user_id not in linked_accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked accounts"
        )
    
    assets = 0
    liabilities = 0
    
    for account in linked_accounts_db[user_id]:
        if account["account_type"] in ["checking", "savings", "investment"]:
            assets += account["current_balance"]
        elif account["account_type"] == "credit":
            liabilities += abs(account["current_balance"])
    
    net_worth = assets - liabilities
    
    return NetWorth(
        total_assets=round(assets, 2),
        total_liabilities=round(liabilities, 2),
        net_worth=round(net_worth, 2),
        change_30_days=round(random.uniform(-5, 10), 1)
    )


@router.get("/monthly", response_model=List[MonthlySpending])
async def get_monthly_spending(
    current_user: User = Depends(get_current_user),
    months: int = 6
):
    """Get monthly spending history."""
    
    user_id = current_user.id
    
    # Generate demo monthly data
    monthly_data = []
    for i in range(months):
        month_date = datetime.utcnow() - timedelta(days=30 * i)
        spending = round(random.uniform(2000, 4000), 2)
        income = round(random.uniform(4000, 7000), 2)
        
        monthly_data.append({
            "month": month_date.strftime("%Y-%m"),
            "spending": spending,
            "income": income
        })
    
    return [MonthlySpending(**m) for m in reversed(monthly_data)]


@router.delete("/accounts/{account_id}")
async def unlink_account(
    account_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unlink a bank account."""
    
    user_id = current_user.id
    
    if user_id not in linked_accounts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked accounts"
        )
    
    for i, account in enumerate(linked_accounts_db[user_id]):
        if account["id"] == account_id:
            deleted = linked_accounts_db[user_id].pop(i)
            # Also delete transactions
            if account_id in transactions_db:
                del transactions_db[account_id]
            return {"message": "Account unlinked"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Account not found"
    )
