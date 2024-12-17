"""
Configuration for settings tests
"""
import pytest

def pytest_configure(config):
    """Configure pytest for settings tests"""
    config.addinivalue_line(
        "markers",
        "settings: mark test as a settings test"
    )

@pytest.fixture(autouse=True)
def skip_db():
    """Skip database setup for settings tests"""
    yield
