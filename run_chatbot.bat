@echo off
title AI Chatbot Server - Keep This Window Open
color 0A
cd /d "F:\ai talk bot"

:start
cls
echo ===============================================
echo       🤖 AI CHATBOT SERVER 🤖
echo ===============================================
echo.
echo ✅ Starting AI Chatbot Server...
echo 🌐 Server URL: http://localhost:5000
echo 📱 Keep this window open to keep server running
echo 🛑 Press Ctrl+C to stop the server
echo.
echo ⏳ Please wait while server starts...
echo.

"F:/ai talk bot/.venv/Scripts/python.exe" app.py

echo.
echo ❌ Server has stopped.
echo.
echo Choose an option:
echo [R] Restart the server
echo [Q] Quit
echo.
set /p choice="Enter your choice (R/Q): "

if /i "%choice%"=="R" goto start
if /i "%choice%"=="Q" goto end

:end
echo.
echo ✅ Chatbot server closed successfully.
echo Press any key to exit...
pause >nul