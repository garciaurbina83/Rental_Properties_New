"""
Settings module for the application
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings class for the application
    """
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/rental_properties"
    database_test_url: str = "postgresql://postgres:postgres@localhost:5432/rental_properties_test"
    database_host: str = "localhost"
    database_port: str = "5432"
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "rental_properties"
    
    # Application settings
    app_name: str = "Rental Properties API"
    app_version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    backend_port: str = "8000"
    
    # Pagination settings
    default_limit: int = 10
    max_limit: int = 100
    
    # Security settings
    secret_key: str = Field(default="test_secret_key_for_development_only", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Clerk settings
    clerk_secret_key: str = "sk_test_mLLXZzeqktoLswvg...psDQw3Mr8pSQ3sYCsvM0JOg"
    clerk_publishable_key: str = "pk_test_cmFwaWQtbW91c2Ut...lcmsuYWNjb3VudHMuZGV2JA"
    
    # CORS settings
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()

def get_settings() -> Settings:
    """
    Returns a cached instance of the settings.
    This ensures we only create one instance of the settings throughout the application.
    """
    return settings
