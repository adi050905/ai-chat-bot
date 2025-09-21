from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from database import db
import uuid
import json
from datetime import timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Secrets and environment
ENVIRONMENT = os.getenv('ENVIRONMENT', os.getenv('FLASK_ENV', 'development')).lower()
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Session cookie hardening
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=int(os.getenv('SESSION_LIFETIME_DAYS', '7')))

# CORS restrictions (only for API routes)
allowed_origins = [o.strip() for o in os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000').split(',') if o.strip()]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

print("🚀 Simple AI Chatbot Starting...")
print(f"  Gemini API: {'✅ Ready' if GEMINI_API_KEY else '❌ Not configured'}")

# Abort startup in production if SECRET_KEY is weak/default
if ENVIRONMENT == 'production' and app.secret_key == 'your-secret-key-change-this-in-production':
    raise SystemExit("SECRET_KEY is not set for production. Set SECRET_KEY in environment.")

def get_gemini_response(message):
    """Get response from Google Gemini"""
    try:
        if not GEMINI_API_KEY:
            return None
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a helpful AI assistant. Respond to: {message}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 150
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return content.strip()
        
        return None
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def get_backup_response(message):
    """Simple backup AI responses"""
    message_lower = message.lower()
    
    if 'hello' in message_lower or 'hi' in message_lower:
        return "Hello! I'm your AI assistant. How can I help you today?"
    elif 'how are you' in message_lower:
        return "I'm doing well, thank you! I'm here to help with any questions you have."
    elif 'name' in message_lower:
        return "I'm your AI chatbot assistant. What would you like to know?"
    elif 'help' in message_lower:
        return "I'm here to help! You can ask me questions or have a conversation."
    elif 'bye' in message_lower:
        return "Goodbye! It was nice chatting with you."
    else:
        return f"I understand you said: '{message}'. I'm a simple backup AI. For better responses, try the Gemini AI option!"

@app.route('/')
def index():
    # Initialize user session if not exists
    if 'user_id' not in session:
        session['user_id'] = db.create_user()
    
    if 'session_id' not in session:
        session['session_id'] = db.create_chat_session(session['user_id'])
    
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Simple AI Chatbot is running!'})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        service = data.get('preferred_service', 'auto')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create user session
        if 'user_id' not in session:
            session['user_id'] = db.create_user()
        
        if 'session_id' not in session:
            session['session_id'] = db.create_chat_session(session['user_id'])
        
        user_id = session['user_id']
        session_id = session['session_id']
        
        # Save user message to database
        db.save_message(session_id, 'user', message, {'service': service})
        
        # Try services based on preference
        if service == 'gemini':
            response = get_gemini_response(message)
            if response:
                # Save AI response to database
                db.save_message(session_id, 'ai', response, {'service': 'Gemini AI'})
                return jsonify({'response': response, 'service': 'Gemini AI'})
            else:
                response = get_backup_response(message)
                db.save_message(session_id, 'ai', response, {'service': 'Backup AI (Gemini failed)'})
                return jsonify({'response': response, 'service': 'Backup AI (Gemini failed)'})
        
        elif service == 'deepseek':
            response = get_backup_response(message)
            db.save_message(session_id, 'ai', response, {'service': 'Backup AI'})
            return jsonify({'response': response, 'service': 'Backup AI'})
        
        else:  # auto
            response = get_gemini_response(message)
            if response:
                db.save_message(session_id, 'ai', response, {'service': 'Gemini AI'})
                return jsonify({'response': response, 'service': 'Gemini AI'})
            else:
                response = get_backup_response(message)
                db.save_message(session_id, 'ai', response, {'service': 'Backup AI'})
                return jsonify({'response': response, 'service': 'Backup AI'})
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'response': 'Sorry, something went wrong. Please try again.', 'service': 'Error Handler'})

@app.route('/api/history', methods=['GET'])
def get_chat_history():
    """Get chat history for current session"""
    try:
        if 'session_id' not in session:
            return jsonify({'history': []})
        
        session_id = session['session_id']
        limit = request.args.get('limit', 50, type=int)
        
        history = db.get_chat_history(session_id, limit)
        return jsonify({'history': history})
    
    except Exception as e:
        print(f"History error: {e}")
        return jsonify({'error': 'Failed to retrieve chat history'}), 500

@app.route('/api/sessions', methods=['GET'])
def get_user_sessions():
    """Get all chat sessions for current user"""
    try:
        if 'user_id' not in session:
            return jsonify({'sessions': []})
        
        user_id = session['user_id']
        sessions = db.get_user_sessions(user_id)
        return jsonify({'sessions': sessions})
    
    except Exception as e:
        print(f"Sessions error: {e}")
        return jsonify({'error': 'Failed to retrieve sessions'}), 500

@app.route('/api/sessions', methods=['POST'])
def create_new_session():
    """Create a new chat session"""
    try:
        if 'user_id' not in session:
            session['user_id'] = db.create_user()
        
        data = request.get_json()
        session_name = data.get('name', 'New Chat')
        
        user_id = session['user_id']
        new_session_id = db.create_chat_session(user_id, session_name)
        
        # DO NOT switch session here. Let the frontend explicitly switch.
        # session['session_id'] = new_session_id
        
        return jsonify({'session_id': new_session_id, 'message': 'New session created'})
    
    except Exception as e:
        print(f"Create session error: {e}")
        return jsonify({'error': 'Failed to create new session'}), 500

@app.route('/api/sessions/<int:session_id>/switch', methods=['POST'])
def switch_session(session_id):
    """Switch to a different chat session"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'No user session'}), 400
        
        # Verify session belongs to user
        user_sessions = db.get_user_sessions(session['user_id'])
        session_ids = [s['id'] for s in user_sessions]
        
        if session_id not in session_ids:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        session['session_id'] = session_id
        return jsonify({'message': 'Session switched successfully'})
    
    except Exception as e:
        print(f"Switch session error: {e}")
        return jsonify({'error': 'Failed to switch session'}), 500

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'No user session'}), 400
        
        # Verify session belongs to user
        user_sessions = db.get_user_sessions(session['user_id'])
        session_ids = [s['id'] for s in user_sessions]
        
        if session_id not in session_ids:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        db.delete_session(session_id)
        
        # If deleted session was current session, create new one
        if session.get('session_id') == session_id:
            session['session_id'] = db.create_chat_session(session['user_id'])
        
        return jsonify({'message': 'Session deleted successfully'})
    
    except Exception as e:
        print(f"Delete session error: {e}")
        return jsonify({'error': 'Failed to delete session'}), 500

@app.route('/api/sessions/<int:session_id>/rename', methods=['PUT'])
def rename_session(session_id):
    """Rename a chat session"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'No user session'}), 400
        
        data = request.get_json()
        new_name = data.get('name', '').strip()
        
        if not new_name:
            return jsonify({'error': 'Name is required'}), 400
        
        # Verify session belongs to user
        user_sessions = db.get_user_sessions(session['user_id'])
        session_ids = [s['id'] for s in user_sessions]
        
        if session_id not in session_ids:
            return jsonify({'error': 'Session not found or access denied'}), 404
        
        db.update_session_name(session_id, new_name)
        return jsonify({'message': 'Session renamed successfully'})
    
    except Exception as e:
        print(f"Rename session error: {e}")
        return jsonify({'error': 'Failed to rename session'}), 500

@app.route('/api/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics"""
    try:
        stats = db.get_database_stats()
        
        # Add user-specific stats
        if 'user_id' in session:
            user_sessions = db.get_user_sessions(session['user_id'])
            stats['user_sessions'] = len(user_sessions)
            stats['user_messages'] = sum(s['message_count'] for s in user_sessions)
        else:
            stats['user_sessions'] = 0
            stats['user_messages'] = 0
        
        return jsonify(stats)
    
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_current_session():
    """Clear current session and start fresh"""
    try:
        session.clear()
        return jsonify({'message': 'Session cleared successfully'})
    
    except Exception as e:
        print(f"Clear session error: {e}")
        return jsonify({'error': 'Failed to clear session'}), 500

@app.route('/api/current-session', methods=['GET'])
def get_current_session():
    """Get current session information"""
    try:
        if 'session_id' not in session:
            return jsonify({'session_id': None})
        
        return jsonify({
            'session_id': session['session_id'],
            'user_id': session.get('user_id')
        })
    
    except Exception as e:
        print(f"Get current session error: {e}")
        return jsonify({'error': 'Failed to get current session'}), 500

# Basic security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    # Only set HSTS when explicitly forced (behind HTTPS proxy)
    if os.getenv('FORCE_HTTPS', 'false').lower() == 'true':
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    # Optional CSP is disabled by default to avoid breaking external assets; enable by setting CSP_DEFAULT
    csp = os.getenv('CONTENT_SECURITY_POLICY')
    if csp:
        response.headers['Content-Security-Policy'] = csp
    return response

if __name__ == '__main__':
    print("🎯 Server starting on http://localhost:5000")
    print("📦 Database: Initialized successfully")
    print("📱 Keep this window open to keep the server running")
    print("🌐 Open your browser to http://localhost:5000 to use the chatbot")
    print("💬 Chat history will be automatically saved")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Display database stats
    stats = db.get_database_stats()
    print(f"📊 Database stats: {stats['users']} users, {stats['sessions']} sessions, {stats['messages']} messages")
    print("-" * 60)
    
    try:
        app.run(
            host='0.0.0.0',  # Accept connections from any IP
            port=5000,
            debug=False,
            use_reloader=False,  # Prevent auto-restart issues
            threaded=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("💡 Try running as administrator or check if port 5000 is free")
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        print("✅ Chatbot shut down successfully")