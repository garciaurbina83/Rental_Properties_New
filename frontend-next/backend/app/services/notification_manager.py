from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from fastapi import WebSocket
from app.models import User, Notification, NotificationType, NotificationStatus
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """Conectar un nuevo cliente WebSocket"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"Nueva conexión WebSocket para usuario {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Desconectar un cliente WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"Conexión WebSocket cerrada para usuario {user_id}")

    async def send_notification(
        self,
        user_id: int,
        notification: Dict[str, Any]
    ):
        """Enviar notificación a un usuario específico"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(notification)
                except Exception as e:
                    logger.error(f"Error enviando notificación: {str(e)}")
                    disconnected.append(websocket)
            
            # Limpiar conexiones cerradas
            for websocket in disconnected:
                self.disconnect(websocket, user_id)

    async def broadcast(
        self,
        notification: Dict[str, Any],
        exclude_user: Optional[int] = None
    ):
        """Enviar notificación a todos los usuarios conectados"""
        disconnected_users = []
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
                
            disconnected = []
            for websocket in connections:
                try:
                    await websocket.send_json(notification)
                except Exception as e:
                    logger.error(f"Error en broadcast: {str(e)}")
                    disconnected.append(websocket)
            
            # Limpiar conexiones cerradas
            for websocket in disconnected:
                self.disconnect(websocket, user_id)
            
            if not self.active_connections[user_id]:
                disconnected_users.append(user_id)
        
        # Limpiar usuarios sin conexiones
        for user_id in disconnected_users:
            del self.active_connections[user_id]

    @staticmethod
    async def create_notification(
        db: Session,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> Notification:
        """Crear una nueva notificación en la base de datos"""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=json.dumps(data) if data else None,
            priority=priority,
            status=NotificationStatus.UNREAD,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
        await db.flush()
        
        return notification

    @staticmethod
    async def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """Marcar una notificación como leída"""
        notification = await db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification and notification.status == NotificationStatus.UNREAD:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            await db.flush()
        
        return notification

    @staticmethod
    async def get_user_notifications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """Obtener notificaciones de un usuario"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.status == NotificationStatus.UNREAD)
        
        return await query.order_by(Notification.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    async def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """Eliminar una notificación"""
        notification = await db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            await db.delete(notification)
            await db.flush()
            return True
        
        return False

# Instancia global del gestor de notificaciones
notification_manager = NotificationManager()
