# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""WebSocket manager for real-time updates."""

from __future__ import annotations

import json
from typing import Dict, Set, Any
from datetime import datetime
import asyncio
from collections import defaultdict


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        # user_id -> set of websocket connections
        self.active_connections: Dict[str, Set[Any]] = defaultdict(set)
        # broadcast connections (admin updates)
        self.broadcast_connections: Set[Any] = set()
    
    async def connect(self, websocket, user_id: str = None):
        """Accept new WebSocket connection."""
        await websocket.accept()
        
        if user_id:
            self.active_connections[user_id].add(websocket)
            print(f"🔗 User {user_id} connected. Total: {len(self.active_connections[user_id])}")
        else:
            self.broadcast_connections.add(websocket)
            print(f"📢 Broadcast connection added. Total: {len(self.broadcast_connections)}")
    
    def disconnect(self, websocket, user_id: str = None):
        """Remove WebSocket connection."""
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            print(f"🔌 User {user_id} disconnected. Remaining: {len(self.active_connections.get(user_id, []))}")
        
        self.broadcast_connections.discard(websocket)
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user."""
        if user_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"❌ Error sending to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def send_broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = set()
        
        for connection in self.broadcast_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"❌ Error broadcasting: {e}")
                disconnected.add(connection)
        
        # Clean up
        for conn in disconnected:
            self.broadcast_connections.discard(conn)
    
    async def notify_user(self, user_id: str, event_type: str, data: Any):
        """Send notification to user."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)
    
    async def notify_goal_update(self, user_id: str, goal_data: dict):
        """Notify goal update."""
        await self.notify_user(user_id, "goal_update", goal_data)
    
    async def notify_task_update(self, user_id: str, task_data: dict):
        """Notify task update."""
        await self.notify_user(user_id, "task_update", task_data)
    
    async def notify_new_notification(self, user_id: str, notification: dict):
        """Notify new notification."""
        await self.notify_user(user_id, "new_notification", notification)
    
    async def notify_finance_update(self, user_id: str, finance_data: dict):
        """Notify finance data update."""
        await self.notify_user(user_id, "finance_update", finance_data)
    
    async def broadcast_announcement(self, announcement: dict):
        """Broadcast announcement to all."""
        message = {
            "type": "announcement",
            "data": announcement,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_broadcast(message)
    
    def get_online_users(self) -> list:
        """Get list of online user IDs."""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, user_id: str = None) -> int:
        """Get connection count."""
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return len(self.active_connections)


# Global connection manager
manager = ConnectionManager()
