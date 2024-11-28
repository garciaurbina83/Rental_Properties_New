from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .core.database import SessionLocal
from .core.security import verify_token
from .core.config import settings

security = HTTPBearer()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Dependency for getting current authenticated user
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user_data = await verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Dependency for getting current user if token is provided, otherwise None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_data = await verify_token(token)
        return user_data
    except:
        return None

def check_admin_access(current_user: dict = Depends(get_current_user)) -> None:
    """
    Dependency for checking admin access
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )

def pagination_params(
    skip: int = 0,
    limit: int = settings.DEFAULT_PAGINATION_LIMIT
) -> tuple[int, int]:
    """
    Dependency for pagination parameters
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    
    if limit < settings.MIN_PAGINATION_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit parameter must be greater than or equal to {settings.MIN_PAGINATION_LIMIT}"
        )
    
    if limit > settings.MAX_PAGINATION_LIMIT:
        limit = settings.MAX_PAGINATION_LIMIT
    
    return skip, limit
