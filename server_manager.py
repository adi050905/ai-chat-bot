#!/usr/bin/env python3
"""
Server health checker and auto-restart utility
"""
import subprocess
import time
import requests
import os
import sys

def check_server_health():
    """Check if the server is responding"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the Flask server"""
    os.chdir(r"F:\ai talk bot")
    python_path = r"F:/ai talk bot/.venv/Scripts/python.exe"
    
    print("🚀 Starting AI Chatbot Server...")
    print("🌐 Will be available at: http://localhost:5000")
    print("🔄 Auto-restart enabled")
    print("-" * 50)
    
    while True:
        process = None
        try:
            # Start the server process
            process = subprocess.Popen([python_path, "app.py"])
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if server is healthy
            if check_server_health():
                print("✅ Server is running and healthy!")
                print("🌐 Open http://localhost:5000 in your browser")
                
                # Wait for the process to finish
                process.wait()
                
            else:
                print("❌ Server failed to start properly")
                if process and process.poll() is None:
                    process.terminate()
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            if process and process.poll() is None:
                process.terminate()
            break
            
        except Exception as e:
            print(f"❌ Error: {e}")
            if process and process.poll() is None:
                process.terminate()
            
        # Ask if user wants to restart
        try:
            restart = input("\n🔄 Server stopped. Restart? (Y/n): ").strip().lower()
            if restart == 'n' or restart == 'no':
                break
        except KeyboardInterrupt:
            break
    
    print("✅ Server shutdown complete")

if __name__ == "__main__":
    start_server()