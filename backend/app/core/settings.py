"""
Settings module for the application
"""
from typing import List
from dataclasses import dataclass
from functools import lru_cache
import os

@dataclass
class Settings:
    """
    Application settings using dataclass for simpler validation
    """
    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/rental_properties"
    database_test_url: str = "postgresql://postgres:postgres@localhost:5432/rental_properties_test"

    # Application settings
    app_name: str = "Rental Properties API"
    api_v1_str: str = "/api/v1"
    
    # Security settings
    secret_key: str = "your_super_secret_key_here"
    access_token_expire_minutes: int = 30
    
    # Authentication settings
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    
    # CORS settings
    backend_cors_origins: List[str] = None
    
    # Pagination settings
    default_limit: int = 10
    min_limit: int = 1
    max_limit: int = 100
    
    # Environment
    debug: bool = False
    environment: str = "development"
    
    def __post_init__(self):
        """Initialize settings from environment variables"""
        # Database settings
        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.database_test_url = os.getenv("DATABASE_TEST_URL", self.database_test_url)
        
        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        
        # Authentication settings
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY", self.clerk_secret_key)
        self.clerk_publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY", self.clerk_publishable_key)
        
        # Set default CORS origins if None
        if self.backend_cors_origins is None:
            self.backend_cors_origins = ["http://localhost:3000", "http://localhost:8000"]
        
        # Environment settings
        self.debug = os.getenv("DEBUG", str(self.debug)).lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", self.environment)

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
