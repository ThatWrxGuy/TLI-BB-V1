# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Authentication API routes."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import secrets
import hashlib

from app.models.user import (
    User, UserCreate, UserRole, OAuthProvider, 
    SubscriptionTier, EmailVerification
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user storage (replace with database in production)
users_db: dict[str, dict] = {}
users_by_email: dict[str, str] = {}  # email -> user_id

# JWT secret (should be in environment variables)
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
    user: User


class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str


class VerifyEmailResponse(BaseModel):
    """Email verification response."""
    message: str
    user: User


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str


class OAuthInitResponse(BaseModel):
    """OAuth initialization response."""
    auth_url: str


class UserResponse(BaseModel):
    """Current user response."""
    user: User
    subscription_tier: str


# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    try:
        salt, pwd_hash = password_hash.split("$")
        return pwd_hash == hashlib.sha256((password + salt).encode()).hexdigest()
    except:
        return False


def create_access_token(user_id: str, email: str, role: str) -> str:
    """Create a JWT access token."""
    import base64
    import json
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }
    
    # Simple base64 encoding (use pyjwt in production)
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"{payload_b64}"


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token."""
    import base64
    import json
    
    try:
        payload_b64 = token.split(".")[0] if "." in token else token
        payload_json = base64.b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)
        
        if datetime.fromisoformat(payload["exp"].replace("Z", "+00:00")) < datetime.utcnow():
            return None
            
        return payload
    except:
        return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    if user_id in users_db:
        return User(**users_db[user_id])
    return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = get_user_by_id(payload["sub"])
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
async def signup(request: SignUpRequest):
    """Register a new user with email/password."""
    
    # Check if user already exists
    if request.email.lower() in users_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user ID and verification token
    user_id = secrets.token_urlsafe(16)
    verification_token = secrets.token_urlsafe(32)
    
    # Create user record
    user_data = {
        "id": user_id,
        "email": request.email.lower(),
        "full_name": request.full_name,
        "password_hash": hash_password(request.password),
        "role": UserRole.USER.value,
        "is_verified": False,
        "is_active": True,
        "subscription_tier": SubscriptionTier.FREE.value,
        "verification_token": verification_token,
        "verification_expires": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    users_db[user_id] = user_data
    users_by_email[request.email.lower()] = user_id
    
    # TODO: Send verification email
    print(f"📧 Verification email would be sent to {request.email}")
    print(f"🔗 Verification link: /auth/verify?token={verification_token}")


# Admin secret key (should be in environment variables)
ADMIN_SECRET_KEY = "busy-bee-admin-2024"


class AdminSignupRequest(BaseModel):
    """Admin signup request."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    admin_secret: str  # Secret key to create admin account


class AdminSignupResponse(BaseModel):
    """Admin signup response."""
    message: str
    user_id: str
    role: str
    admin_panel_url: str


@router.post("/admin-signup", response_model=AdminSignupResponse)
async def admin_signup(request: AdminSignupRequest):
    """Register a new admin account. Requires secret key."""
    
    # Verify admin secret
    if request.admin_secret != ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret key"
        )
    
    # Check if user already exists
    if request.email.lower() in users_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create admin user ID and verification token
    user_id = secrets.token_urlsafe(16)
    verification_token = secrets.token_urlsafe(32)
    
    # Create admin user record
    user_data = {
        "id": user_id,
        "email": request.email.lower(),
        "full_name": request.full_name or "Admin",
        "password_hash": hash_password(request.password),
        "role": UserRole.ADMIN.value,  # Admin role
        "is_verified": True,  # Admins are auto-verified
        "is_active": True,
        "subscription_tier": SubscriptionTier.ENTERPRISE.value,  # Enterprise for admins
        "verification_token": None,
        "verification_expires": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    users_db[user_id] = user_data
    users_by_email[request.email.lower()] = user_id
    
    print(f"👑 Admin account created: {request.email} (ID: {user_id})")
    
    return AdminSignupResponse(
        message="Admin account created successfully",
        user_id=user_id,
        role="admin",
        admin_panel_url="/admin"
    )


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email/password."""
    
    user_id = users_by_email.get(form_data.username.lower())
    
    if not user_id or user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user_data = users_db[user_id]
    
    if not verify_password(form_data.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user_data["last_login_at"] = datetime.utcnow().isoformat()
    
    # Create token
    access_token = create_access_token(
        user_id=user_data["id"],
        email=user_data["email"],
        role=user_data["role"]
    )
    
    user = User(**user_data)
    
    return LoginResponse(
        access_token=access_token,
        user=user
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user."""
    # In a real system, you'd invalidate the token
    return {"message": "Successfully logged out"}


@router.post("/verify", response_model=VerifyEmailResponse)
async def verify_email(request: VerifyEmailRequest):
    """Verify user email address."""
    
    # Find user by verification token
    user_id = None
    for uid, udata in users_db.items():
        if udata.get("verification_token") == request.token:
            user_id = uid
            break
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    user_data = users_db[user_id]
    
    # Check if token expired
    if user_data.get("verification_expires"):
        exp = datetime.fromisoformat(user_data["verification_expires"])
        if exp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token expired"
            )
    
    # Mark as verified
    user_data["is_verified"] = True
    user_data["verification_token"] = None
    user_data["verification_expires"] = None
    user_data["updated_at"] = datetime.utcnow().isoformat()
    
    user = User(**user_data)
    
    return VerifyEmailResponse(
        message="Email verified successfully!",
        user=user
    )


@router.post("/resend-verification")
async def resend_verification(email: EmailStr):
    """Resend verification email."""
    
    user_id = users_by_email.get(email.lower())
    
    if not user_id:
        # Don't reveal if email exists
        return {"message": "If the email exists, a verification link will be sent"}
    
    user_data = users_db[user_id]
    
    if user_data.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
    verification_token = secrets.token_urlsafe(32)
    user_data["verification_token"] = verification_token
    user_data["verification_expires"] = (datetime.utcnow() + timedelta(hours=24)).isoformat()
    
    # TODO: Send verification email
    print(f"📧 Verification email resent to {email}")
    print(f"🔗 Verification link: /auth/verify?token={verification_token}")
    
    return {"message": "Verification email sent"}


@router.post("/password-reset-request")
async def request_password_reset(email: EmailStr):
    """Request password reset."""
    
    user_id = users_by_email.get(email.lower())
    
    if not user_id:
        # Don't reveal if email exists
        return {"message": "If the account exists, a reset link will be sent"}
    
    user_data = users_db[user_id]
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user_data["password_reset_token"] = reset_token
    user_data["password_reset_expires"] = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    # TODO: Send password reset email
    print(f"📧 Password reset email sent to {email}")
    print(f"🔗 Reset link: /auth/password-reset/confirm?token={reset_token}")
    
    return {"message": "Password reset email sent"}


@router.post("/password-reset-confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest):
    """Confirm password reset with new password."""
    
    # Find user by reset token
    user_id = None
    for uid, udata in users_db.items():
        if udata.get("password_reset_token") == request.token:
            user_id = uid
            break
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    user_data = users_db[user_id]
    
    # Check if token expired
    if user_data.get("password_reset_expires"):
        exp = datetime.fromisoformat(user_data["password_reset_expires"])
        if exp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token expired"
            )
    
    # Update password
    user_data["password_hash"] = hash_password(request.new_password)
    user_data["password_reset_token"] = None
    user_data["password_reset_expires"] = None
    user_data["updated_at"] = datetime.utcnow().isoformat()
    
    return {"message": "Password reset successfully"}


# ==================== OAUTH ROUTES ====================

@router.get("/oauth/{provider}", response_model=OAuthInitResponse)
async def oauth_init(provider: str):
    """Initiate OAuth flow."""
    
    valid_providers = ["github", "google"]
    if provider.lower() not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Valid: {valid_providers}"
        )
    
    # OAuth configuration (should be in environment variables)
    oauth_configs = {
        "github": {
            "client_id": "github_client_id",
            "auth_url": "https://github.com/login/oauth/authorize",
            "scope": "user:email read:user"
        },
        "google": {
            "client_id": "google_client_id",
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "scope": "openid email profile"
        }
    }
    
    config = oauth_configs[provider.lower()]
    state = secrets.token_urlsafe(16)
    
    # Build authorization URL
    auth_url = f"{config['auth_url']}?client_id={config['client_id']}&redirect_uri=http://localhost:8000/auth/oauth/callback&response_type=code&scope={config['scope']}&state={state}"
    
    return OAuthInitResponse(auth_url=auth_url)


@router.get("/oauth/callback")
async def oauth_callback(code: str, state: str, provider: str):
    """OAuth callback handler."""
    
    # TODO: Exchange code for access token
    # TODO: Get user info from provider
    # TODO: Create or update user
    
    # For now, return placeholder
    return {"message": "OAuth callback received", "code": code, "provider": provider}


# ==================== USER ROUTES ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    
    return UserResponse(
        user=current_user,
        subscription_tier=current_user.subscription_tier
    )


@router.get("/users", response_model=list[User])
async def list_users(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List users (admin only)."""
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = list(users_db.values())[skip:skip+limit]
    return [User(**u) for u in users]
