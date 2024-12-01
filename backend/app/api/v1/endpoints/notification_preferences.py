from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.core.cache import notification_cache
from app.schemas import notification_preference as schemas
from app.crud import notification as notification_crud

router = APIRouter()

@router.get("/preferences", response_model=schemas.NotificationPreferenceResponse)
async def get_notification_preferences(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get current user's notification preferences.
    """
    # Try to get from cache first
    preferences = await notification_cache.get_user_preferences(current_user.id)
    if not preferences:
        # If not in cache, get from database
        preferences = await notification_crud.get_user_preferences(db, current_user.id)
        if preferences:
            # Cache the preferences
            await notification_cache.set_user_preferences(current_user.id, preferences)
        else:
            # Create default preferences if none exist
            preferences_data = schemas.NotificationPreferenceCreate(
                user_id=current_user.id,
                preferences=schemas.create_default_preferences()
            )
            preferences = await notification_crud.create_user_preferences(
                db,
                preferences_data
            )
            await notification_cache.set_user_preferences(current_user.id, preferences)
    
    return preferences

@router.put("/preferences", response_model=schemas.NotificationPreferenceResponse)
async def update_notification_preferences(
    preferences_update: schemas.NotificationPreferenceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Update current user's notification preferences.
    """
    # Get existing preferences
    current_preferences = await notification_crud.get_user_preferences(
        db,
        current_user.id
    )
    if not current_preferences:
        raise HTTPException(
            status_code=404,
            detail="Notification preferences not found"
        )

    # Update preferences
    updated_preferences = await notification_crud.update_user_preferences(
        db,
        current_preferences,
        preferences_update
    )

    # Invalidate cache
    await notification_cache.invalidate_user_cache(current_user.id)

    return updated_preferences

@router.post("/preferences/reset", response_model=schemas.NotificationPreferenceResponse)
async def reset_notification_preferences(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Reset current user's notification preferences to default values.
    """
    preferences_data = schemas.NotificationPreferenceCreate(
        user_id=current_user.id,
        preferences=schemas.create_default_preferences()
    )
    
    # Update or create preferences
    preferences = await notification_crud.get_user_preferences(db, current_user.id)
    if preferences:
        preferences = await notification_crud.update_user_preferences(
            db,
            preferences,
            preferences_data
        )
    else:
        preferences = await notification_crud.create_user_preferences(
            db,
            preferences_data
        )

    # Invalidate cache
    await notification_cache.invalidate_user_cache(current_user.id)

    return preferences

@router.get("/preferences/channels", response_model=List[str])
async def get_available_channels():
    """
    Get list of available notification channels.
    """
    from app.schemas.notification import NotificationChannel
    return [channel.value for channel in NotificationChannel]

@router.get("/preferences/types", response_model=List[str])
async def get_notification_types():
    """
    Get list of available notification types.
    """
    from app.schemas.notification import NotificationType
    return [type.value for type in NotificationType]
