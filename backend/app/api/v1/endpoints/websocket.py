from typing import Optional
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from app.core.websocket import notification_ws_manager
from app.core.security import get_current_user_ws
from app.models.user import User

router = APIRouter()

@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time notifications.
    """
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    try:
        # Authenticate user
        current_user = await get_current_user_ws(token)
        if not current_user:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return

        # Connect websocket
        await notification_ws_manager.connect(websocket, current_user.id)

        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_json()
                
                # Handle ping messages to keep connection alive
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

        except Exception as e:
            # Handle disconnection
            notification_ws_manager.disconnect(websocket, current_user.id)

    except Exception as e:
        await websocket.close(code=4002, reason="Authentication failed")
        return
