# AI Chatbot PowerShell Startup Script
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "       🤖 AI CHATBOT SERVER 🤖" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Starting AI Chatbot Server..." -ForegroundColor Green
Write-Host "🌐 Server URL: http://localhost:5000" -ForegroundColor Yellow
Write-Host "📱 Keep this window open to keep server running" -ForegroundColor Yellow
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Change to chatbot directory
Set-Location "F:\ai talk bot"

# Function to start server
function Start-ChatbotServer {
    try {
        Write-Host "⏳ Starting server..." -ForegroundColor Yellow
        & "F:/ai talk bot/.venv/Scripts/python.exe" app.py
    }
    catch {
        Write-Host "❌ Error starting server: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Try running as administrator or check if port 5000 is free" -ForegroundColor Yellow
    }
}

# Start the server
do {
    Start-ChatbotServer
    
    Write-Host ""
    Write-Host "❌ Server has stopped." -ForegroundColor Red
    Write-Host ""
    $restart = Read-Host "Do you want to restart the server? (Y/N)"
    
} while ($restart -eq "Y" -or $restart -eq "y")

Write-Host ""
Write-Host "✅ Chatbot server closed successfully." -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")