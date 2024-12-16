from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.maintenance import MaintenanceTicket, TicketStatus, TicketPriority
from app.schemas.maintenance import (
    MaintenanceTicketCreate,
    MaintenanceTicketUpdate,
    MaintenanceTicket as MaintenanceTicketSchema,
    MaintenanceTicketDetail
)
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/tickets/", response_model=MaintenanceTicketSchema)
def create_maintenance_ticket(
    ticket: MaintenanceTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo ticket de mantenimiento"""
    db_ticket = MaintenanceTicket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Enviar notificación
    notification_service = NotificationService(db)
    notification_service.send_maintenance_notification(
        user_id=current_user.id,
        title=f"Nuevo ticket de mantenimiento: {ticket.title}",
        message=f"Se ha creado un nuevo ticket de mantenimiento con prioridad {ticket.priority}",
        priority=ticket.priority
    )
    
    return db_ticket

@router.get("/tickets/", response_model=List[MaintenanceTicketDetail])
def get_maintenance_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    property_id: Optional[int] = None,
    tenant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de tickets de mantenimiento con filtros opcionales"""
    query = db.query(MaintenanceTicket)
    
    if status:
        query = query.filter(MaintenanceTicket.status == status)
    if priority:
        query = query.filter(MaintenanceTicket.priority == priority)
    if property_id:
        query = query.filter(MaintenanceTicket.property_id == property_id)
    if tenant_id:
        query = query.filter(MaintenanceTicket.tenant_id == tenant_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/tickets/{ticket_id}", response_model=MaintenanceTicketDetail)
def get_maintenance_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener detalles de un ticket específico"""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    return ticket

@router.put("/tickets/{ticket_id}", response_model=MaintenanceTicketSchema)
def update_maintenance_ticket(
    ticket_id: int,
    ticket_update: MaintenanceTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar un ticket de mantenimiento"""
    db_ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = ticket_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    
    db.commit()
    db.refresh(db_ticket)
    
    # Enviar notificación de actualización
    notification_service = NotificationService(db)
    notification_service.send_maintenance_notification(
        user_id=current_user.id,
        title=f"Actualización de ticket: {db_ticket.title}",
        message=f"El ticket ha sido actualizado. Nuevo estado: {db_ticket.status}",
        priority=db_ticket.priority
    )
    
    return db_ticket

@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar un ticket de mantenimiento"""
    db_ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    db.delete(db_ticket)
    db.commit()
    
    return None

@router.post("/tickets/{ticket_id}/close", response_model=MaintenanceTicketSchema)
def close_maintenance_ticket(
    ticket_id: int,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cerrar un ticket de mantenimiento"""
    db_ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    db_ticket.status = TicketStatus.CLOSED
    db_ticket.resolved_date = datetime.utcnow()
    db_ticket.description += f"\n\nResolución: {resolution_notes}"
    
    db.commit()
    db.refresh(db_ticket)
    
    # Enviar notificación de cierre
    notification_service = NotificationService(db)
    notification_service.send_maintenance_notification(
        user_id=current_user.id,
        title=f"Ticket cerrado: {db_ticket.title}",
        message=f"El ticket ha sido cerrado con la siguiente resolución: {resolution_notes}",
        priority=db_ticket.priority
    )
    
    return db_ticket
