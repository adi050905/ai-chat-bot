import sqlite3
import datetime
from typing import List, Dict, Optional, Union
import json
import os

class ChatDatabase:
    def __init__(self, db_path: str = "chatbot.db"):
        # Allow overriding via environment variable
        env_db = os.getenv("DATABASE_PATH")
        self.db_path = env_db if env_db else db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_name TEXT DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                message_type TEXT CHECK(message_type IN ('user', 'ai')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                setting_key TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, setting_key)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized at {os.path.abspath(self.db_path)}")
    
    def create_user(self, username: str = "Anonymous", email: Optional[str] = None) -> int:
        """Create a new user and return user ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email)
                VALUES (?, ?)
            ''', (username, email))
            user_id = cursor.lastrowid
            if user_id is None:
                raise Exception("Failed to create user")
            conn.commit()
            print(f"✅ User created: {username} (ID: {user_id})")
            return user_id
        except sqlite3.IntegrityError:
            # User already exists, get existing user ID
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            user_id = result[0] if result else 1  # Fallback to user ID 1
            return user_id
        finally:
            conn.close()
    
    def create_chat_session(self, user_id: int, session_name: str = "New Chat") -> int:
        """Create a new chat session and return session ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_sessions (user_id, session_name)
            VALUES (?, ?)
        ''', (user_id, session_name))
        
        session_id = cursor.lastrowid
        if session_id is None:
            raise Exception("Failed to create chat session")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Chat session created: {session_name} (ID: {session_id})")
        return session_id
    
    def save_message(self, session_id: int, message_type: str, content: str, metadata: Optional[Dict] = None) -> int:
        """Save a message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO messages (session_id, message_type, content, metadata)
            VALUES (?, ?, ?, ?)
        ''', (session_id, message_type, content, metadata_json))
        
        message_id = cursor.lastrowid
        if message_id is None:
            raise Exception("Failed to save message")
        
        # Update session timestamp
        cursor.execute('''
            UPDATE chat_sessions 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_chat_history(self, session_id: int, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, message_type, content, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            metadata = json.loads(row[4]) if row[4] else {}
            messages.append({
                'id': row[0],
                'type': row[1],
                'content': row[2],
                'timestamp': row[3],
                'metadata': metadata
            })
        
        conn.close()
        return messages
    
    def get_user_sessions(self, user_id: int) -> List[Dict]:
        """Get all chat sessions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cs.id, cs.session_name, cs.created_at, cs.updated_at,
                   COUNT(m.id) as message_count,
                   MAX(m.timestamp) as last_message_time
            FROM chat_sessions cs
            LEFT JOIN messages m ON cs.id = m.session_id
            WHERE cs.user_id = ?
            GROUP BY cs.id, cs.session_name, cs.created_at, cs.updated_at
            ORDER BY cs.updated_at DESC
        ''', (user_id,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'updated_at': row[3],
                'message_count': row[4],
                'last_message_time': row[5]
            })
        
        conn.close()
        return sessions
    
    def update_session_name(self, session_id: int, new_name: str):
        """Update session name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chat_sessions 
            SET session_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_name, session_id))
        
        conn.commit()
        conn.close()
    
    def delete_session(self, session_id: int):
        """Delete a chat session and all its messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        # Delete session
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        conn.close()
        print(f"✅ Session {session_id} deleted")
    
    def save_user_setting(self, user_id: int, key: str, value: str):
        """Save user setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_settings (user_id, setting_key, setting_value)
            VALUES (?, ?, ?)
        ''', (user_id, key, value))
        
        conn.commit()
        conn.close()
    
    def get_user_setting(self, user_id: int, key: str, default=None):
        """Get user setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT setting_value FROM user_settings
            WHERE user_id = ? AND setting_key = ?
        ''', (user_id, key))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else default
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chat_sessions')
        session_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages')
        message_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'users': user_count,
            'sessions': session_count,
            'messages': message_count
        }

# Initialize database instance
db = ChatDatabase()

if __name__ == "__main__":
    # Test database functionality
    print("🧪 Testing database functionality...")
    
    # Create test user
    user_id = db.create_user("TestUser", "test@example.com")
    
    # Create test session
    session_id = db.create_chat_session(user_id, "Test Chat")
    
    # Save test messages
    db.save_message(session_id, "user", "Hello, AI!")
    db.save_message(session_id, "ai", "Hello! How can I help you today?", {"model": "gemini"})
    
    # Get chat history
    history = db.get_chat_history(session_id)
    print(f"📝 Chat history: {len(history)} messages")
    
    # Get user sessions
    sessions = db.get_user_sessions(user_id)
    print(f"💬 User sessions: {len(sessions)}")
    
    # Get stats
    stats = db.get_database_stats()
    print(f"📊 Database stats: {stats}")
    
    print("✅ Database test completed successfully!")