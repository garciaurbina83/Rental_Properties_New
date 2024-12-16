from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceTicket, TicketStatus, TicketPriority
from app.models.user import User
from app.schemas.maintenance import MaintenanceTicketCreate, MaintenanceTicketUpdate
from app.services.notification_service import NotificationService

class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def create_ticket(self, ticket_data: MaintenanceTicketCreate, user: User) -> MaintenanceTicket:
        """Crear un nuevo ticket de mantenimiento"""
        db_ticket = MaintenanceTicket(**ticket_data.model_dump())
        self.db.add(db_ticket)
        self.db.commit()
        self.db.refresh(db_ticket)
        
        # Enviar notificación
        self._send_ticket_notification(
            db_ticket,
            "Nuevo ticket de mantenimiento",
            f"Se ha creado un nuevo ticket de mantenimiento: {db_ticket.title}"
        )
        
        return db_ticket

    def get_tickets(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        property_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> List[MaintenanceTicket]:
        """Obtener tickets de mantenimiento con filtros"""
        query = self.db.query(MaintenanceTicket)
        
        if status:
            query = query.filter(MaintenanceTicket.status == status)
        if priority:
            query = query.filter(MaintenanceTicket.priority == priority)
        if property_id:
            query = query.filter(MaintenanceTicket.property_id == property_id)
        if tenant_id:
            query = query.filter(MaintenanceTicket.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()

    def get_ticket(self, ticket_id: int) -> Optional[MaintenanceTicket]:
        """Obtener un ticket específico por ID"""
        return self.db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()

    def update_ticket(self, ticket_id: int, ticket_update: MaintenanceTicketUpdate) -> Optional[MaintenanceTicket]:
        """Actualizar un ticket existente"""
        db_ticket = self.get_ticket(ticket_id)
        if not db_ticket:
            return None
        
        # Guardar el estado anterior para comparación
        previous_status = db_ticket.status
        
        # Actualizar campos
        update_data = ticket_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ticket, field, value)
        
        self.db.commit()
        self.db.refresh(db_ticket)
        
        # Enviar notificación si el estado cambió
        if previous_status != db_ticket.status:
            self._send_ticket_notification(
                db_ticket,
                "Actualización de estado de ticket",
                f"El ticket {db_ticket.title} ha cambiado de estado a: {db_ticket.status.value}"
            )
        
        return db_ticket

    def close_ticket(self, ticket_id: int, resolution_notes: str) -> Optional[MaintenanceTicket]:
        """Cerrar un ticket de mantenimiento"""
        db_ticket = self.get_ticket(ticket_id)
        if not db_ticket:
            return None
        
        db_ticket.status = TicketStatus.CLOSED
        db_ticket.resolved_date = datetime.utcnow()
        db_ticket.description += f"\n\nResolución: {resolution_notes}"
        
        self.db.commit()
        self.db.refresh(db_ticket)
        
        # Enviar notificación
        self._send_ticket_notification(
            db_ticket,
            "Ticket cerrado",
            f"El ticket {db_ticket.title} ha sido cerrado. Resolución: {resolution_notes}"
        )
        
        return db_ticket

    def delete_ticket(self, ticket_id: int) -> bool:
        """Eliminar un ticket de mantenimiento"""
        db_ticket = self.get_ticket(ticket_id)
        if not db_ticket:
            return False
        
        self.db.delete(db_ticket)
        self.db.commit()
        return True

    def get_overdue_tickets(self) -> List[MaintenanceTicket]:
        """Obtener tickets vencidos"""
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.due_date < datetime.utcnow(),
            MaintenanceTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        ).all()

    def get_upcoming_maintenance(self, days: int = 7) -> List[MaintenanceTicket]:
        """Obtener mantenimientos programados próximos"""
        future_date = datetime.utcnow() + timedelta(days=days)
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.due_date <= future_date,
            MaintenanceTicket.due_date >= datetime.utcnow(),
            MaintenanceTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        ).all()

    def _send_ticket_notification(self, ticket: MaintenanceTicket, title: str, message: str):
        """Enviar notificación relacionada con un ticket"""
        # Notificar al inquilino si existe
        if ticket.tenant_id:
            self.notification_service.send_maintenance_notification(
                user_id=ticket.tenant_id,
                title=title,
                message=message,
                priority=ticket.priority
            )
        
        # Notificar al administrador de la propiedad
        # Aquí podrías agregar lógica para obtener el ID del administrador de la propiedad
        # y enviarle la notificación también
