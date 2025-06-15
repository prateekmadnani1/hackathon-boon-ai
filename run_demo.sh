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

# Create results directory if it doesn't exist
mkdir -p results

# Check if data/examples directory has any image files
IMAGE_COUNT=$(find data/examples -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" | wc -l)

if [ $IMAGE_COUNT -eq 0 ]; then
  echo "⚠️ No image files found in data/examples directory."
  echo "For best results, please save your example document images to this directory:"
  echo "  - data/examples/freight_invoice_steves_trucking.jpg"
  echo "  - data/examples/rate_confirmation_bennett.jpg"
  echo "  - data/examples/bill_of_lading_linbis.jpg"
  echo ""
  echo "However, the demo will still run with mock data."
  echo ""
fi

# Run the app in mock mode (uses mock data instead of calling LLM APIs)
echo "🚀 Running Boon Entity Mapper Demo..."
echo "This demo uses mock data and doesn't require API keys."
echo ""

python src/main.py process data/examples --output results --model mock --verbose

echo ""
echo "✅ Demo completed successfully!"
echo "Results have been saved to the 'results' directory."
echo ""
echo "To view the visualization, open the HTML files in your web browser:"
echo "  - results/*/visualization.html"
echo ""
echo "In a real run, you would need to:"
echo "1. Configure your API keys in .env file"
echo "2. Run: python src/main.py process data/examples --output results"
