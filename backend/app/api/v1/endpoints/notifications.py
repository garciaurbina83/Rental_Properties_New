from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.core.cache import notification_cache
from app.schemas.notification import NotificationResponse, NotificationStatus
from app.crud import notification as notification_crud

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retrieve user's notifications with pagination.
    """
    return await notification_crud.get_user_notifications(
        db,
        current_user.id,
        skip=skip,
        limit=limit
    )

@router.get("/unread/count", response_model=int)
async def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get count of unread notifications.
    """
    # Try to get from cache first
    count = await notification_cache.get_unread_count(current_user.id)
    if count is None:
        count = await notification_crud.get_unread_count(db, current_user.id)
        await notification_cache.set_unread_count(current_user.id, count)
    return count

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Mark a notification as read.
    """
    notification = await notification_crud.mark_as_read(
        db,
        notification_id,
        current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    
    # Invalidate unread count cache
    await notification_cache.invalidate_user_cache(current_user.id)
    
    return {"status": "success"}

@router.post("/read/all")
async def mark_all_as_read(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Mark all notifications as read.
    """
    count = await notification_crud.mark_all_as_read(db, current_user.id)
    
    # Invalidate unread count cache
    await notification_cache.invalidate_user_cache(current_user.id)
    
    return {"status": "success", "marked_count": count}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Delete a notification.
    """
    notification = await notification_crud.get(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    await notification_crud.remove(db, id=notification_id)
    
    # Invalidate unread count cache if notification was unread
    if not notification.read_at:
        await notification_cache.invalidate_user_cache(current_user.id)
    
    return {"status": "success"}
