import os
import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Import your FastAPI app and database session
from backend.main import app
from backend.database import SessionLocal
from backend.app.core.config import settings

# Fixture for the FastAPI TestClient
@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

# Fixture for the database session
@pytest.fixture(scope="function")
def db() -> Generator:
    connection = SessionLocal()
    try:
        yield connection
    finally:
        connection.close()

# Fixture for authenticated client
@pytest.fixture(scope="function")
def auth_client(client: TestClient) -> Generator[TestClient, Any, None]:
    # Add your authentication logic here
    # For example:
    # response = client.post("/auth/login", json={"username": "test", "password": "test"})
    # token = response.json()["access_token"]
    # client.headers["Authorization"] = f"Bearer {token}"
    yield client

# Fixture for Selenium WebDriver (Chrome)
@pytest.fixture(scope="function")
def selenium_driver() -> Generator:
    chrome_options = Options()
    if os.getenv("CI") == "true":
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    try:
        yield driver
    finally:
        driver.quit()

# Fixture for test data
@pytest.fixture(scope="function")
def test_data() -> dict:
    return {
        "property": {
            "address": "123 Test St",
            "type": "Apartment",
            "rentAmount": 1000,
            "status": "Available"
        },
        "tenant": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        }
    }

# Fixture for cleanup after tests
@pytest.fixture(autouse=True)
def cleanup_after_test(db: Session) -> None:
    yield
    # Clean up logic here
    # For example:
    # db.execute("TRUNCATE TABLE properties CASCADE")
    # db.execute("TRUNCATE TABLE tenants CASCADE")
    # db.commit()
