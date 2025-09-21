#!/usr/bin/env python3
"""
Simple server starter that handles common Flask issues
"""
import os
import sys
import time

def start_server():
    """Start the Flask server with proper error handling"""
    try:
        # Change to the correct directory
        os.chdir(r"F:\ai talk bot")
        
        # Import and run the Flask app
        from app import app
        
        print("🚀 Starting AI Chatbot Server...")
        print("📡 Server will be available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run with simple configuration that works reliably
        app.run(
            host='localhost',  # Use localhost instead of 127.0.0.1
            port=5000,
            debug=False,
            use_reloader=False,  # Prevent restart issues
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("� Error details:")
        import traceback
        traceback.print_exc()
        print("\n�💡 Try running again or check the app.py file")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    start_server()