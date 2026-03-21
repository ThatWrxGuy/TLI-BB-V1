# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Authentication API routes with database support."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DbSession
import secrets
import hashlib
import jwt

from app.database import get_db
from app.models.database import User, UserRole, SubscriptionTier

router = APIRouter(prefix="/auth", tags=["Authentication"])

# JWT secret (should be in environment variables)
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ==================== HELPERS ====================

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def get_user_by_email(db: DbSession, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: DbSession, user_id: str) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


# ==================== REQUEST/RESPONSE MODELS ====================

class SignUpRequest(BaseModel):
    """Signup request."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class SignUpResponse(BaseModel):
    """Signup response."""
    message: str
    user_id: str
    verification_required: bool = True


class LoginResponse(BaseModel):
    """Login response."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User response."""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    subscription_tier: str
    is_verified: bool


class AdminSignupRequest(BaseModel):
    """Admin signup request."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    admin_secret: str


class AdminSignupResponse(BaseModel):
    """Admin signup response."""
    message: str
    user_id: str
    role: str
    admin_panel_url: str


# ==================== DEPENDENCIES ====================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: DbSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role to access endpoint."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ==================== AUTH ROUTES ====================

@router.post("/signup", response_model=SignUpResponse)
async def signup(request: SignUpRequest, db: DbSession = Depends(get_db)):
    """Register a new user with email/password."""
    
    # Check if user already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user ID and verification token
    user_id = secrets.token_urlsafe(16)
    verification_token = secrets.token_urlsafe(32)
    
    # Create user record
    user = User(
        id=user_id,
        email=request.email.lower(),
        full_name=request.full_name,
        password_hash=hash_password(request.password),
        role=UserRole.USER,
        is_verified=False,
        is_active=True,
        subscription_tier=SubscriptionTier.FREE,
        verification_token=verification_token,
        verification_expires=datetime.utcnow() + timedelta(hours=24),
    )
    
    db.add(user)
    db.commit()
    
    # TODO: Send verification email
    print(f"📧 Verification email would be sent to {request.email}")
    print(f"🔗 Verification link: /auth/verify?token={verification_token}")
    
    return SignUpResponse(
        message="Account created successfully. Please verify your email.",
        user_id=user_id,
        verification_required=True
    )


# Admin secret key
ADMIN_SECRET_KEY = "busy-bee-admin-2024"


@router.post("/admin-signup", response_model=AdminSignupResponse)
async def admin_signup(request: AdminSignupRequest, db: DbSession = Depends(get_db)):
    """Register a new admin account. Requires secret key."""
    
    # Verify admin secret
    if request.admin_secret != ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret key"
        )
    
    # Check if user already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create admin user
    user = User(
        id=secrets.token_urlsafe(16),
        email=request.email.lower(),
        full_name=request.full_name or "Admin",
        password_hash=hash_password(request.password),
        role=UserRole.ADMIN,
        is_verified=True,
        is_active=True,
        subscription_tier=SubscriptionTier.ENTERPRISE,
        verification_token=None,
        verification_expires=None,
    )
    
    db.add(user)
    db.commit()
    
    print(f"👑 Admin account created: {request.email}")
    
    return AdminSignupResponse(
        message="Admin account created successfully",
        user_id=user.id,
        role="admin",
        admin_panel_url="/admin"
    )


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DbSession = Depends(get_db)):
    """Login with email/password."""
    
    user = get_user_by_email(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "subscription_tier": user.subscription_tier.value,
        }
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (invalidate token client-side)."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        subscription_tier=current_user.subscription_tier.value,
        is_verified=current_user.is_verified,
    )


@router.post("/verify")
async def verify_email(token: str, db: DbSession = Depends(get_db)):
    """Verify email with token."""
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification token"
        )
    
    if user.verification_expires and user.verification_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token expired"
        )
    
    user.is_verified = True
    user.verification_token = None
    user.verification_expires = None
    db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/password-reset-request")
async def request_password_reset(email: str, db: DbSession = Depends(get_db)):
    """Request password reset."""
    user = get_user_by_email(db, email)
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        # In production, send email with reset link
        print(f"🔑 Password reset for {email}: /auth/password-reset?token={reset_token}")
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset-confirm")
async def reset_password_confirm(token: str, new_password: str, db: DbSession = Depends(get_db)):
    """Reset password with token."""
    # In production, look up token from database
    return {"message": "Password reset successfully"}


# OAuth routes (placeholder)
@router.get("/oauth/{provider}")
async def oauth_redirect(provider: str):
    """Redirect to OAuth provider."""
    return {"message": f"OAuth {provider} not configured"}
