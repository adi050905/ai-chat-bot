@echo off
echo Starting AI Chatbot...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo Error: Could not activate virtual environment
    echo Please make sure .venv exists in the current directory
    pause
    exit /b 1
)

echo Virtual environment activated successfully!
echo.

REM Install/update dependencies
echo Checking dependencies...
pip install -r requirements.txt

REM Start the Flask application
echo.
echo Starting Flask server...
echo The chatbot will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause