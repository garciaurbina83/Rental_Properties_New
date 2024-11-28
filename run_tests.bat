@echo off
echo Running tests...

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Install test dependencies
pip install -r requirements-dev.txt

REM Run unit tests
echo Running unit tests...
pytest tests/unit -v

REM Run integration tests
echo Running integration tests...
pytest tests/integration -v

REM Run e2e tests
echo Running e2e tests...
pytest tests/e2e -v

REM Generate coverage report
echo Generating coverage report...
coverage report
coverage html

echo All tests completed!
pause
