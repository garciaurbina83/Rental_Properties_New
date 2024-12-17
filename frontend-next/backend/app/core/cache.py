import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class NotificationCache:
    """
    Cache manager for notification-related data.
    """
    PREFERENCES_KEY = "notification_preferences:{user_id}"
    UNREAD_COUNT_KEY = "unread_notifications_count:{user_id}"
    CACHE_TTL = 300  # 5 minutes

    @staticmethod
    async def get_user_preferences(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached user notification preferences.
        """
        key = NotificationCache.PREFERENCES_KEY.format(user_id=user_id)
        return await FastAPICache.get(key)

    @staticmethod
    async def set_user_preferences(user_id: int, preferences: Dict[str, Any]):
        """
        Cache user notification preferences.
        """
        key = NotificationCache.PREFERENCES_KEY.format(user_id=user_id)
        await FastAPICache.set(key, preferences, expire=NotificationCache.CACHE_TTL)

    @staticmethod
    async def get_unread_count(user_id: int) -> Optional[int]:
        """
        Get cached unread notifications count.
        """
        key = NotificationCache.UNREAD_COUNT_KEY.format(user_id=user_id)
        return await FastAPICache.get(key)

    @staticmethod
    async def set_unread_count(user_id: int, count: int):
        """
        Cache unread notifications count.
        """
        key = NotificationCache.UNREAD_COUNT_KEY.format(user_id=user_id)
        await FastAPICache.set(key, count, expire=NotificationCache.CACHE_TTL)

    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """
        Invalidate all cached data for a user.
        """
        keys = [
            NotificationCache.PREFERENCES_KEY.format(user_id=user_id),
            NotificationCache.UNREAD_COUNT_KEY.format(user_id=user_id)
        ]
        for key in keys:
            await FastAPICache.delete(key)

def setup_cache():
    """
    Initialize cache backend.
    """
    try:
        redis_backend = RedisBackend(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        FastAPICache.init(redis_backend, prefix="notification-cache:")
        logger.info("Cache backend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize cache backend: {str(e)}")

notification_cache = NotificationCache()
