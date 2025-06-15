#!/bin/bash

# Activate virtual environment if not already activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "Activating virtual environment..."
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
  else
    # Unix/Linux/MacOS
    source venv/bin/activate
  fi
fi

# Run the import test
echo "Running import test..."
python -m tests.test_import

# Check exit code
if [ $? -eq 0 ]; then
  echo "✓ Import test passed! You're ready to run the main application."
  echo "Next steps:"
  echo "1. Make sure your example document images are in data/examples/"
  echo "2. Configure your API keys in .env"
  echo "3. Run: python src/main.py process data/examples --output results"
else
  echo "✗ Import test failed."
  echo "Please check the error message above and make sure all dependencies are installed:"
  echo "pip install -r requirements.txt"
fi
