from typing import List, Optional
import os
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Project Info
    APP_NAME: str = "Rental Properties API"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BACKEND_PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/rental_properties"
    DATABASE_TEST_URL: str = "postgresql://postgres:postgres@localhost:5432/rental_properties_test"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "rental_properties"
    
    # Authentication settings
    SECRET_KEY: str = "your-secret-key"
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Clerk settings
    CLERK_SECRET_KEY: str = "your_clerk_secret_key"
    CLERK_PUBLISHABLE_KEY: str = "pk_test_cmFwaWQtbW91c2Ut...lcmsuYWNjb3VudHMuZGV2JA"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # Pagination settings
    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100
    MIN_LIMIT: int = 1
    
    # Optional Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_email_password"
    EMAILS_FROM_EMAIL: str = "your_email@gmail.com"
    EMAILS_FROM_NAME: str = "Rental Properties"
    
    # Optional Frontend settings
    REACT_APP_API_URL: str = "http://localhost:8000"
    REACT_APP_CLERK_PUBLISHABLE_KEY: str = "your_clerk_publishable_key"
    REACT_APP_ENVIRONMENT: str = "development"
    
    # Optional AWS settings
    AWS_ACCESS_KEY_ID: str = "your_aws_access_key"
    AWS_SECRET_ACCESS_KEY: str = "your_aws_secret_key"
    AWS_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str = "your_bucket_name"
    
    # Optional Monitoring settings
    PROMETHEUS_BASIC_AUTH_USER: str = "admin"
    PROMETHEUS_BASIC_AUTH_PASSWORD: str = "admin"
    GF_SECURITY_ADMIN_USER: str = "admin"
    GF_SECURITY_ADMIN_PASSWORD: str = "admin"
    GF_SERVER_ROOT_URL: str = "http://localhost:3000/grafana"
    ALERTMANAGER_SLACK_WEBHOOK: str = "your_slack_webhook_url"
    ALERTMANAGER_SLACK_CHANNEL: str = "#alerts"
    
    # Optional Nginx settings
    NGINX_HOST: str = "localhost"
    SSL_CERTIFICATE_PATH: str = "/etc/nginx/ssl/server.crt"
    SSL_CERTIFICATE_KEY_PATH: str = "/etc/nginx/ssl/server.key"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("ENVIRONMENT") == "testing" else ".env",
        env_file_encoding="utf-8",
        validate_default=True,
        extra="allow",
        case_sensitive=True,
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        str_to_lower=False,
        str_to_upper=False,
        strict=False,
        allow_inf_nan=False,
        allow_mutation=True,
        frozen=False,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
        env_nested_delimiter="__",
        env_prefix="",
        protected_namespaces=(),
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = Settings()
