"""
Módulo para la gestión de notificaciones en tiempo real.
"""

from typing import Dict, List, Optional
import asyncio
from fastapi import WebSocket
from datetime import datetime
import json

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.notification_history: Dict[str, List[Dict]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Conecta un nuevo cliente WebSocket.
        
        Args:
            websocket (WebSocket): Conexión WebSocket
            user_id (str): ID del usuario
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        # Envía notificaciones no leídas al conectarse
        await self.send_unread_notifications(user_id)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Desconecta un cliente WebSocket.
        
        Args:
            websocket (WebSocket): Conexión WebSocket
            user_id (str): ID del usuario
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
    async def send_notification(self, user_id: str, notification_type: str, data: Dict):
        """
        Envía una notificación a un usuario específico.
        
        Args:
            user_id (str): ID del usuario
            notification_type (str): Tipo de notificación
            data (Dict): Datos de la notificación
        """
        notification = {
            "type": notification_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        
        # Guarda la notificación en el historial
        if user_id not in self.notification_history:
            self.notification_history[user_id] = []
        self.notification_history[user_id].append(notification)
        
        # Envía a todas las conexiones activas del usuario
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(notification))
                except:
                    await self.disconnect(connection, user_id)
                    
    async def send_unread_notifications(self, user_id: str):
        """
        Envía todas las notificaciones no leídas a un usuario.
        
        Args:
            user_id (str): ID del usuario
        """
        if user_id in self.notification_history:
            unread = [n for n in self.notification_history[user_id] if not n["read"]]
            if user_id in self.active_connections:
                for connection in self.active_connections[user_id]:
                    try:
                        for notification in unread:
                            await connection.send_text(json.dumps(notification))
                    except:
                        await self.disconnect(connection, user_id)
                        
    async def mark_as_read(self, user_id: str, notification_ids: List[str]):
        """
        Marca notificaciones como leídas.
        
        Args:
            user_id (str): ID del usuario
            notification_ids (List[str]): Lista de IDs de notificaciones
        """
        if user_id in self.notification_history:
            for notification in self.notification_history[user_id]:
                if notification.get("id") in notification_ids:
                    notification["read"] = True
                    
    async def broadcast_to_role(self, role: str, notification_type: str, data: Dict):
        """
        Envía una notificación a todos los usuarios con un rol específico.
        
        Args:
            role (str): Rol de usuario
            notification_type (str): Tipo de notificación
            data (Dict): Datos de la notificación
        """
        # Aquí deberías implementar la lógica para obtener todos los usuarios con el rol especificado
        # y enviar la notificación a cada uno
        pass

# Instancia global del gestor de notificaciones
notification_manager = NotificationManager()

# Tipos de notificaciones
NOTIFICATION_TYPES = {
    "MAINTENANCE_REQUEST": "maintenance.request",
    "PAYMENT_REMINDER": "payment.reminder",
    "CONTRACT_EXPIRATION": "contract.expiration",
    "PROPERTY_UPDATE": "property.update",
    "SYSTEM_ALERT": "system.alert"
}
