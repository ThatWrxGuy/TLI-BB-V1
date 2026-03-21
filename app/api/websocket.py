# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""WebSocket API for real-time updates."""

from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import json
import jwt
from datetime import datetime

from app.api.websocket_manager import manager
from app.models.database import User

router = APIRouter(tags=["WebSocket"])

# JWT secret (should match auth.py)
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_user_from_token(token: str) -> Optional[User]:
    """Get user from WebSocket connection token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            from app.database import SessionLocal
            from app.models.database import User as DBUser
            db = SessionLocal()
            try:
                user = db.query(DBUser).filter(DBUser.id == user_id).first()
                return user
            finally:
                db.close()
    except Exception as e:
        print(f"WebSocket auth error: {e}")
    return None


# ==================== WEBSOCKET ENDPOINTS ====================

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """Main WebSocket endpoint for real-time updates."""
    
    user = None
    
    # Try to authenticate
    if token:
        user = await get_user_from_token(token)
    
    user_id = user.id if user else None
    
    # Connect
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "data": {
                "user_id": user_id,
                "message": "Connected to Busy Bee real-time updates"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                # Handle ping/pong
                if msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Handle subscription to events
                elif msg_type == "subscribe":
                    # User wants to subscribe to specific event types
                    pass
                
                # Handle echo (for testing)
                elif msg_type == "echo":
                    await websocket.send_json({
                        "type": "echo",
                        "data": message.get("data"),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"},
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        print(f"🔌 Client disconnected: {user_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


# ==================== BROADCAST ENDPOINTS (for admin/system) ====================

@router.post("/ws/broadcast")
async def broadcast_message(
    event_type: str,
    message: str,
    target: str = "all"  # all, online, specific_user_id
):
    """
    Broadcast a message to connected clients.
    This endpoint can be called by the backend to push updates.
    """
    from app.api.websocket_manager import manager
    
    if target == "all":
        await manager.broadcast_announcement({
            "event_type": event_type,
            "message": message
        })
        return {
            "status": "broadcast_sent",
            "connections": len(manager.broadcast_connections)
        }
    
    elif target == "online":
        online_users = manager.get_online_users()
        for user_id in online_users:
            await manager.notify_user(user_id, event_type, {"message": message})
        return {
            "status": "sent_to_online",
            "user_count": len(online_users)
        }
    
    else:
        # Specific user
        await manager.notify_user(target, event_type, {"message": message})
        return {
            "status": "sent",
            "user_id": target
        }


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status."""
    from app.api.websocket_manager import manager
    
    return {
        "status": "active",
        "total_connections": len(manager.broadcast_connections),
        "online_users": manager.get_online_users(),
        "timestamp": datetime.utcnow().isoformat()
    }
