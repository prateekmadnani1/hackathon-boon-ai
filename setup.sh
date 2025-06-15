#!/bin/bash

# Create and activate virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source venv/bin/activate
fi

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys"
fi

# Create necessary directories
echo "Creating project directories..."
mkdir -p results

echo "Setup complete! Virtual environment is activated."
echo "To activate this environment in the future, run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
