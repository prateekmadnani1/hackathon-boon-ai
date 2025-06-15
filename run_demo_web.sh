#!/bin/bash
# Script to run the web demo of the Entity Mapper application

# Set the current directory to the script directory
cd "$(dirname "$0")" || exit

# Set environment variables
export PYTHONPATH="$PWD"
export FLASK_APP="src/app.py"
export FLASK_ENV="development"
export DEFAULT_MODEL="gpt-4o"  # Can be overridden by .env file
export PORT=8080  # Use port 8080 instead of 5000

# Check if the virtual environment exists
if [ -d "venv" ]; then
    # Activate the virtual environment
    echo "Activating virtual environment..."
    if [ -f "venv/bin/activate" ]; then
        source "venv/bin/activate"
    elif [ -f "venv/Scripts/activate" ]; then
        source "venv/Scripts/activate"
    else
        echo "Error: Could not find activation script for the virtual environment."
        exit 1
    fi
else
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if the .env file exists and load it
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source ".env"
    set +a
else
    echo "Warning: .env file not found. Using default environment variables."
fi

# Create uploads directory if it doesn't exist
mkdir -p data/uploads

# Install Flask if not already installed
if ! pip show flask > /dev/null 2>&1; then
    echo "Installing Flask..."
    pip install flask flask-wtf
fi

# Start the Flask server
echo "Starting the web demo at http://localhost:${PORT}"
echo "Press Ctrl+C to stop the server"
python -m flask run --host=0.0.0.0 --port=${PORT} 