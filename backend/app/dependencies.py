"""
Dependencies for FastAPI application
"""
from typing import AsyncGenerator, Optional, Tuple
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .core.database import SessionLocal
from .core.security import verify_token
from .core.settings import Settings

settings = Settings()
security = HTTPBearer()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions
    """
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Dependency for getting current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    user = await verify_token(token)
    
    if not user:
        raise credentials_exception
        
    return user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """
    Dependency for getting current user if token is provided, otherwise None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user = await verify_token(token)
    return user

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page")
) -> Tuple[int, int]:
    """
    Get pagination parameters
    Returns tuple of (skip, limit)
    """
    skip = (page - 1) * page_size
    return skip, page_size
