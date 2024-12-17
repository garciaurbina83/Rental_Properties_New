import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.schemas.notification import NotificationResponse

logger = logging.getLogger(__name__)

class NotificationWebsocketManager:
    def __init__(self):
        # Store active connections: user_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Connect a user's websocket.
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected to notifications websocket")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Disconnect a user's websocket.
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from notifications websocket")

    async def send_notification(self, user_id: int, notification: NotificationResponse):
        """
        Send a notification to a specific user through all their active connections.
        """
        if user_id not in self.active_connections:
            return

        # Convert notification to dict for JSON serialization
        notification_data = notification.dict()
        
        disconnected = set()
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(notification_data)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                disconnected.add(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def broadcast_notification(self, user_ids: Set[int], notification: NotificationResponse):
        """
        Broadcast a notification to multiple users.
        """
        for user_id in user_ids:
            await self.send_notification(user_id, notification)

    async def send_unread_count(self, user_id: int, count: int):
        """
        Send unread notification count to a user.
        """
        if user_id not in self.active_connections:
            return

        count_data = {"type": "unread_count", "count": count}
        
        disconnected = set()
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(count_data)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending unread count to user {user_id}: {str(e)}")
                disconnected.add(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

notification_ws_manager = NotificationWebsocketManager()
