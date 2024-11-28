# Testing Documentation

This directory contains all the tests for the Rental Properties application. The tests are organized into different categories and levels of testing.

## Directory Structure

```
tests/
├── integration/     # Integration tests
├── e2e/            # End-to-end tests
├── fixtures/       # Test fixtures and data
├── utils/          # Test utilities and helpers
├── conftest.py     # Shared pytest fixtures
├── pytest.ini      # Pytest configuration
└── README.md       # This file
```

## Development Setup

### Prerequisites
1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Set up test database:
```bash
createdb rental_properties_test
alembic upgrade head
```

## Test Categories

### Integration Tests (`/integration`)
- API endpoints testing
- Database operations
- Service layer interactions
- Authentication flows
- Uses `pytest-mock` for mocking external services

### End-to-End Tests (`/e2e`)
- Selenium WebDriver for browser automation
- Complete user workflows
- UI element verification
- Cross-component integration
- Parallel testing with `pytest-xdist`

## Testing Tools

### Core Testing
- `pytest`: Test runner and framework
- `pytest-cov`: Code coverage reporting
- `pytest-mock`: Mocking functionality
- `pytest-xdist`: Parallel test execution
- `pytest-asyncio`: Async test support
- `faker`: Test data generation

### Browser Automation
- `selenium`: Browser automation
- `webdriver-manager`: WebDriver management

### Code Quality
- `black`: Code formatting
- `flake8`: Code linting
- `isort`: Import sorting
- `mypy`: Static type checking
- `pylint`: Code analysis
- `bandit`: Security checks

## Running Tests

### Basic Test Commands

All tests:
```bash
pytest
```

Specific test categories:
```bash
pytest tests/integration  # Integration tests
pytest tests/e2e         # E2E tests
pytest -m api            # API tests only
```

### Advanced Test Options

Parallel testing:
```bash
pytest -n auto  # Uses pytest-xdist
```

With coverage:
```bash
pytest --cov=backend --cov=frontend --cov-report=html
```

Generate test data:
```python
from faker import Faker
fake = Faker()

test_data = {
    "name": fake.name(),
    "email": fake.email(),
    "address": fake.address()
}
```

## Test Markers

```python
@pytest.mark.integration    # Integration tests
@pytest.mark.e2e           # End-to-end tests
@pytest.mark.slow          # Slow tests
@pytest.mark.api           # API tests
@pytest.mark.ui           # UI tests
@pytest.mark.auth         # Authentication tests
@pytest.mark.db          # Database tests
```

## Writing Tests

### Best Practices
1. Use fixtures from `conftest.py`
2. Implement proper cleanup
3. Use descriptive test names
4. Follow AAA pattern (Arrange-Act-Assert)
5. Keep tests isolated
6. Use appropriate markers
7. Generate test data with Faker
8. Run tests in parallel when possible

### Example Test with Mocking
```python
import pytest
from faker import Faker

fake = Faker()

@pytest.mark.integration
def test_create_property(auth_client, mocker):
    # Arrange
    mock_service = mocker.patch('services.property_service.create')
    property_data = {
        "address": fake.address(),
        "price": fake.random_number(5)
    }
    
    # Act
    response = auth_client.post("/api/properties/", json=property_data)
    
    # Assert
    assert response.status_code == 201
    mock_service.assert_called_once_with(property_data)
```

## Documentation

Generate documentation:
```bash
mkdocs serve  # Local development
mkdocs build  # Build static site
```

## CI/CD Integration

The test suite runs in CI with:
- Parallel test execution
- Coverage reporting
- Code quality checks
- Security scanning

## Troubleshooting

### Common Issues

1. **Database Connection**
   ```bash
   # Verify database
   psql -l | grep rental_properties_test
   
   # Reset database
   dropdb rental_properties_test && createdb rental_properties_test
   alembic upgrade head
   ```

2. **Selenium Issues**
   ```bash
   # Update webdriver
   webdriver-manager update
   
   # Run in headless mode
   pytest tests/e2e --headless
   ```

3. **Test Isolation**
   ```python
   @pytest.mark.usefixtures("cleanup_database")
   def test_something():
       # Test with clean database
       pass
   ```

### Debug Tools
- Use `debugpy` for Python debugging
- Use `ipython` for interactive debugging
- Enable pytest verbose mode: `pytest -vv`
