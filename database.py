import json
import os
import datetime as dt
from typing import List, Dict, Optional

from sqlalchemy import (
    create_engine, String, Text, ForeignKey, DateTime, func, UniqueConstraint
)
from sqlalchemy.orm import (
    declarative_base, relationship, sessionmaker, Mapped, mapped_column
)
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[Optional[str]] = mapped_column(String, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    last_active: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    session_name: Mapped[str] = mapped_column(String, default="New Chat")
    created_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[Optional[dt.datetime]] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    message_type: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")


class UserSetting(Base):
    __tablename__ = "user_settings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    setting_key: Mapped[str] = mapped_column(String, nullable=False)
    setting_value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, server_default=func.current_timestamp())
    __table_args__ = (
        UniqueConstraint('user_id', 'setting_key', name='uq_user_setting_key'),
        {"sqlite_autoincrement": True},
    )

class ChatDatabase:
    def __init__(self, db_path: str = "chatbot.db"):
        url = os.getenv("DATABASE_URL")
        if url:
            self.engine = create_engine(url, pool_pre_ping=True)
            self.using_url = url
        else:
            # Allow overriding via environment variable path for local SQLite
            env_db = os.getenv("DATABASE_PATH") or db_path
            self.using_url = f"sqlite:///{env_db}"
            self.engine = create_engine(self.using_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.init_database()

    def init_database(self):
        Base.metadata.create_all(self.engine)
        if self.using_url.startswith("sqlite"):
            print(f"✅ Database initialized at {self.using_url}")
        else:
            print(f"✅ Database initialized (URL) {self.using_url}")
    
    def create_user(self, username: str = "Anonymous", email: Optional[str] = None) -> int:
        with self.SessionLocal() as s:
            user = User(username=username, email=email)
            try:
                s.add(user)
                s.commit()
            except IntegrityError:
                s.rollback()
                # User exists; fetch id
                existing = s.query(User).filter_by(username=username).first()
                return existing.id if existing else 1
            return user.id
    
    def create_chat_session(self, user_id: int, session_name: str = "New Chat") -> int:
        with self.SessionLocal() as s:
            cs = ChatSession(user_id=user_id, session_name=session_name)
            s.add(cs)
            s.commit()
            print(f"✅ Chat session created: {session_name} (ID: {cs.id})")
            return cs.id
    
    def save_message(self, session_id: int, message_type: str, content: str, metadata: Optional[Dict] = None) -> int:
        with self.SessionLocal() as s:
            m = Message(
                session_id=session_id,
                message_type=message_type,
                content=content,
                metadata=json.dumps(metadata) if metadata else None,
            )
            s.add(m)
            # update session updated_at
            cs = s.query(ChatSession).filter_by(id=session_id).first()
            if cs:
                cs.updated_at = dt.datetime.utcnow()
            s.commit()
            return int(m.id)
    
    def get_chat_history(self, session_id: int, limit: int = 50) -> List[Dict]:
        with self.SessionLocal() as s:
            rows: List[Message] = (
                s.query(Message)
                .filter_by(session_id=session_id)
                .order_by(Message.timestamp.asc())
                .limit(limit)
                .all()
            )
            out: List[Dict] = []
            for r in rows:
                meta = json.loads(r.metadata) if (r.metadata is not None) else {}
                out.append({
                    'id': int(r.id),
                    'type': r.message_type,
                    'content': r.content,
                    'timestamp': r.timestamp.isoformat() if (r.timestamp is not None) else None,
                    'metadata': meta,
                })
            return out
    
    def get_user_sessions(self, user_id: int) -> List[Dict]:
        with self.SessionLocal() as s:
            # counts and last message time via subqueries
            msg_count = (
                s.query(Message.session_id, func.count(Message.id).label('cnt'))
                .group_by(Message.session_id)
                .subquery()
            )
            last_msg = (
                s.query(Message.session_id, func.max(Message.timestamp).label('last'))
                .group_by(Message.session_id)
                .subquery()
            )
            q = (
                s.query(
                    ChatSession.id,
                    ChatSession.session_name,
                    ChatSession.created_at,
                    ChatSession.updated_at,
                    func.coalesce(msg_count.c.cnt, 0),
                    last_msg.c.last,
                )
                .outerjoin(msg_count, ChatSession.id == msg_count.c.session_id)
                .outerjoin(last_msg, ChatSession.id == last_msg.c.session_id)
                .filter(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
            )
            out: List[Dict] = []
            for row in q.all():  # type: ignore[assignment]
                out.append({
                    'id': int(row[0]),
                    'name': row[1],
                    'created_at': row[2].isoformat() if (row[2] is not None) else None,
                    'updated_at': row[3].isoformat() if (row[3] is not None) else None,
                    'message_count': int(row[4] or 0),
                    'last_message_time': row[5].isoformat() if (row[5] is not None) else None,
                })
            return out
    
    def update_session_name(self, session_id: int, new_name: str):
        with self.SessionLocal() as s:
            cs = s.query(ChatSession).filter_by(id=session_id).first()
            if cs:
                cs.session_name = new_name
                cs.updated_at = dt.datetime.utcnow()
                s.commit()
    
    def delete_session(self, session_id: int):
        with self.SessionLocal() as s:
            cs = s.query(ChatSession).filter_by(id=session_id).first()
            if cs:
                s.delete(cs)
                s.commit()
                print(f"✅ Session {session_id} deleted")
    
    def save_user_setting(self, user_id: int, key: str, value: str):
        with self.SessionLocal() as s:
            existing = (
                s.query(UserSetting)
                .filter_by(user_id=user_id, setting_key=key)
                .first()
            )
            if existing:
                existing.setting_value = value
            else:
                s.add(UserSetting(user_id=user_id, setting_key=key, setting_value=value))
            s.commit()
    
    def get_user_setting(self, user_id: int, key: str, default=None):
        with self.SessionLocal() as s:
            us = s.query(UserSetting).filter_by(user_id=user_id, setting_key=key).first()
            return us.setting_value if us else default
    
    def get_database_stats(self) -> Dict:
        with self.SessionLocal() as s:
            users = s.query(func.count(User.id)).scalar() or 0
            sessions = s.query(func.count(ChatSession.id)).scalar() or 0
            messages = s.query(func.count(Message.id)).scalar() or 0
            return {"users": users, "sessions": sessions, "messages": messages}

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