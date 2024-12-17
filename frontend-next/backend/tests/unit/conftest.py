"""
Configuration for unit tests
"""
import pytest

def pytest_configure(config):
    """Configure pytest for unit tests"""
    config.addinivalue_line(
        "markers",
        "unit: mark test as a unit test"
    )
