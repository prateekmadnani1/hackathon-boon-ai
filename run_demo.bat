@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Create results directory if it doesn't exist
if not exist results mkdir results

REM Check if data/examples directory has any image files
set IMG_COUNT=0
for %%f in (data\examples\*.jpg data\examples\*.jpeg data\examples\*.png) do set /a IMG_COUNT+=1

if %IMG_COUNT% EQU 0 (
    echo.
    echo WARNING: No image files found in data/examples directory.
    echo For best results, please save your example document images to this directory:
    echo   - data/examples/freight_invoice_steves_trucking.jpg
    echo   - data/examples/rate_confirmation_bennett.jpg
    echo   - data/examples/bill_of_lading_linbis.jpg
    echo.
    echo However, the demo will still run with mock data.
    echo.
)

REM Run the app in mock mode (uses mock data instead of calling LLM APIs)
echo Running Boon Entity Mapper Demo...
echo This demo uses mock data and doesn't require API keys.
echo.

python src/main.py process data/examples --output results --model mock --verbose

echo.
echo Demo completed successfully!
echo Results have been saved to the 'results' directory.
echo.
echo To view the visualization, open the HTML files in your web browser:
echo   - results/*/visualization.html
echo.
echo In a real run, you would need to:
echo 1. Configure your API keys in .env file
echo 2. Run: python src/main.py process data/examples --output results
