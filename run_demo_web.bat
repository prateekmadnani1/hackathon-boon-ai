@echo off
REM Script to run the web demo of the Entity Mapper application

REM Set the current directory to the script directory
cd /d "%~dp0"

REM Set environment variables
set PYTHONPATH=%cd%
set FLASK_APP=src/app.py
set FLASK_ENV=development
set DEFAULT_MODEL=gpt-4o
set PORT=8080

REM Check if the virtual environment exists
if exist "venv" (
    REM Activate the virtual environment
    echo Activating virtual environment...
    if exist "venv\Scripts\activate.bat" (
        call "venv\Scripts\activate.bat"
    ) else (
        echo Error: Could not find activation script for the virtual environment.
        exit /b 1
    )
) else (
    echo Error: Virtual environment not found. Please run setup.bat first.
    exit /b 1
)

REM Check if the .env file exists and load it
if exist ".env" (
    echo Loading environment variables from .env file...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
) else (
    echo Warning: .env file not found. Using default environment variables.
)

REM Create uploads directory if it doesn't exist
if not exist "data\uploads" (
    mkdir "data\uploads"
)

REM Install Flask if not already installed
pip show flask >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing Flask...
    pip install flask flask-wtf
)

REM Start the Flask server
echo Starting the web demo at http://localhost:%PORT%
echo Press Ctrl+C to stop the server
python -m flask run --host=0.0.0.0 --port=%PORT% 