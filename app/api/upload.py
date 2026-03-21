# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""File upload API routes."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.models.database import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/upload", tags=["File Upload"])

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
AVATARS_DIR = os.path.join(UPLOAD_DIR, "avatars")
FILES_DIR = os.path.join(UPLOAD_DIR, "files")

# Ensure directories exist
os.makedirs(AVATARS_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# ==================== RESPONSE MODELS ====================

class UploadResponse(BaseModel):
    """Upload response."""
    file_id: str
    filename: str
    url: str
    size: int
    content_type: str


class FileListResponse(BaseModel):
    """File list response."""
    files: list[dict]
    count: int


# ==================== UTILITIES ====================

def get_file_extension(filename: str) -> str:
    """Get file extension."""
    return os.path.splitext(filename)[1].lower()


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename."""
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"


def validate_image(file: UploadFile) -> None:
    """Validate image file."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )


def validate_file(file: UploadFile) -> None:
    """Validate general file."""
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
        )


# ==================== AVATAR UPLOAD ====================

@router.post("/avatar", response_model=UploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload user avatar image."""
    
    # Validate file type
    validate_image(file)
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename or "avatar.jpg")
    file_path = os.path.join(AVATARS_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Generate URL
    file_id = str(uuid.uuid4())
    url = f"/upload/avatars/{filename}"
    
    # Update user's avatar URL in database (if using database)
    # current_user.avatar_url = url
    # db.commit()
    
    return UploadResponse(
        file_id=file_id,
        filename=filename,
        url=url,
        size=len(contents),
        content_type=file.content_type
    )


@router.delete("/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_user)
):
    """Delete user avatar."""
    
    # In production, delete from database and storage
    return {"message": "Avatar deleted successfully"}


# ==================== FILE UPLOAD ====================

@router.post("/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload a general file."""
    
    # Validate file type
    validate_file(file)
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename or "file")
    file_path = os.path.join(FILES_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Generate URL
    file_id = str(uuid.uuid4())
    url = f"/upload/files/{filename}"
    
    return UploadResponse(
        file_id=file_id,
        filename=filename,
        url=url,
        size=len(contents),
        content_type=file.content_type
    )


@router.get("/files", response_model=FileListResponse)
async def list_files(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List user's uploaded files."""
    
    # In production, query from database
    # For demo, return empty list
    return FileListResponse(
        files=[],
        count=0
    )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an uploaded file."""
    
    # In production, verify ownership and delete from storage + database
    return {"message": "File deleted successfully"}


# ==================== SERVE FILES ====================

@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    """Serve avatar image."""
    file_path = os.path.join(AVATARS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(file_path)


@router.get("/files/{filename}")
async def get_file(filename: str):
    """Serve uploaded file."""
    file_path = os.path.join(FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(file_path)
