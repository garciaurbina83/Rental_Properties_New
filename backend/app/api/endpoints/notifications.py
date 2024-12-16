from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import User, Notification, NotificationType, NotificationStatus
from app.services.notification_manager import notification_manager
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationOut
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Endpoint WebSocket para notificaciones en tiempo real"""
    try:
        # TODO: Implementar autenticación de WebSocket
        await notification_manager.connect(websocket, user_id)
        
        try:
            while True:
                # Mantener la conexión viva
                data = await websocket.receive_text()
                
                # Procesar mensajes del cliente si es necesario
                if data == "ping":
                    await websocket.send_text("pong")
                
        except WebSocketDisconnect:
            notification_manager.disconnect(websocket, user_id)
            
    except Exception as e:
        logger.error(f"Error en conexión WebSocket: {str(e)}")
        if websocket.client_state.connected:
            await websocket.close()

@router.get("/", response_model=List[NotificationOut])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener notificaciones del usuario actual"""
    return await notification_manager.get_user_notifications(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar una notificación como leída"""
    notification = await notification_manager.mark_as_read(
        db,
        notification_id,
        current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    
    return {"status": "success"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una notificación"""
    success = await notification_manager.delete_notification(
        db,
        notification_id,
        current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    
    return {"status": "success"}

@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar todas las notificaciones como leídas"""
    notifications = await notification_manager.get_user_notifications(
        db,
        current_user.id,
        unread_only=True
    )
    
    for notification in notifications:
        await notification_manager.mark_as_read(db, notification.id, current_user.id)
    
    return {"status": "success", "count": len(notifications)}
