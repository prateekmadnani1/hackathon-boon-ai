@echo off
echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing required packages...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your API keys
)

echo Creating project directories...
if not exist results mkdir results

echo Setup complete! Virtual environment is activated.
echo To activate this environment in the future, run: venv\Scripts\activate.bat
