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
    model_config = SettingsConfigDict(extra='allow')

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
    
    # Redis settings
    redis_host: str = "redis"
    redis_port: str = "6379"
    redis_password: str = ""
    redis_db: str = "0"
    
    # SMTP settings
    smtp_tls: str = "True"
    smtp_port: str = "587"
    smtp_host: str = "smtp.gmail.com"
    smtp_user: str = "your_email@gmail.com"
    smtp_password: str = "your_email_password"
    
    # Email settings
    emails_from_email: str = "your_email@gmail.com"
    emails_from_name: str = "Rental Properties"
    
    # AWS settings
    aws_access_key_id: str = "your_aws_access_key"
    aws_secret_access_key: str = "your_aws_secret_key"
    aws_region: str = "us-east-1"
    aws_bucket_name: str = "your_bucket_name"
    
    # React app settings
    react_app_api_url: str = "http://localhost:8000"
    react_app_clerk_publishable_key: str = "your_clerk_publishable_key"
    react_app_environment: str = "development"
    
    # Prometheus settings
    prometheus_basic_auth_user: str = "admin"
    prometheus_basic_auth_password: str = "admin"
    
    # Grafana settings
    gf_security_admin_user: str = "admin"
    gf_security_admin_password: str = "admin"
    gf_server_root_url: str = "http://localhost:3000/grafana"
    
    # Alertmanager settings
    alertmanager_slack_webhook: str = "your_slack_webhook_url"
    alertmanager_slack_channel: str = "#alerts"
    
    # Nginx settings
    nginx_host: str = "localhost"
    ssl_certificate_path: str = "/etc/nginx/ssl/server.crt"
    ssl_certificate_key_path: str = "/etc/nginx/ssl/server.key"
    
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
