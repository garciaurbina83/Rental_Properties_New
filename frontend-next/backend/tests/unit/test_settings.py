"""
Tests for the settings module
"""
import os
import pytest
from app.core.settings import Settings, get_settings

def test_default_settings():
    """Test default settings values"""
    settings = Settings()
    
    assert settings.app_name == "Rental Properties API"
    assert settings.api_v1_str == "/api/v1"
    assert settings.environment == "development"
    assert settings.debug is False

def test_environment_override():
    """Test environment variables override settings"""
    # Set test environment variables
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["DEBUG"] = "true"
    os.environ["ENVIRONMENT"] = "testing"
    
    settings = Settings()
    
    assert settings.secret_key == "test_secret_key"
    assert settings.debug is True
    assert settings.environment == "testing"
    
    # Clean up environment
    del os.environ["SECRET_KEY"]
    del os.environ["DEBUG"]
    del os.environ["ENVIRONMENT"]

def test_settings_cache():
    """Test that settings are properly cached"""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2  # Should be the same instance due to caching

def test_cors_origins_default():
    """Test CORS origins default initialization"""
    settings = Settings()
    assert isinstance(settings.backend_cors_origins, list)
    assert len(settings.backend_cors_origins) == 2
    assert "http://localhost:3000" in settings.backend_cors_origins
    assert "http://localhost:8000" in settings.backend_cors_origins

def test_pagination_settings():
    """Test pagination settings"""
    settings = Settings()
    
    assert settings.default_limit == 10
    assert settings.min_limit == 1
    assert settings.max_limit == 100
    assert settings.min_limit <= settings.default_limit <= settings.max_limit
