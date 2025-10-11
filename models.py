from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from datetime import datetime
import json

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'roboto_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    replit_user_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship to user data
    roboto_data = db.relationship('UserData', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class UserData(db.Model):
    __tablename__ = 'roboto_user_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('roboto_users.id'), nullable=False)

    # Roboto conversation data
    chat_history = db.Column(db.JSON, default=lambda: [])
    learned_patterns = db.Column(db.JSON, default=lambda: {})
    user_preferences = db.Column(db.JSON, default=lambda: {})
    emotional_history = db.Column(db.JSON, default=lambda: [])
    memory_system_data = db.Column(db.JSON, default=lambda: {})

    # Current state
    current_emotion: Mapped[str] = mapped_column(String(50), default='curious')
    current_user_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Custom personality (max 3000 characters, permanent)
    custom_personality: Mapped[str] = mapped_column(db.Text, nullable=True)

    # Metadata with different names to avoid conflict
    data_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserData for User {self.user_id}>'

class ConversationSession(db.Model):
    __tablename__ = 'conversation_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False, index=True)

    # Session data
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    message_count = db.Column(db.Integer, default=0)

    # Session context
    context_data = db.Column(db.JSON, default=dict)

    def __repr__(self):
        return f'<ConversationSession {self.session_id}>'

class MemoryEntry(db.Model):
    __tablename__ = 'memory_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    memory_id = db.Column(db.String(32), nullable=False, index=True)

    # Memory content
    content = db.Column(db.Text, nullable=False)
    memory_type = db.Column(db.String(50), default='episodic')
    importance_score = db.Column(db.Float, default=0.5)
    emotional_valence = db.Column(db.Float, default=0.0)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    access_count = db.Column(db.Integer, default=0)

    # Additional data
    entry_metadata = db.Column(db.JSON, default=dict)

    def __repr__(self):
        return f'<MemoryEntry {self.memory_id}>'

class IntegrationSettings(db.Model):
    __tablename__ = 'integration_settings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('roboto_users.id'), nullable=False)
    integration_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    settings_data = db.Column(db.JSON, default=lambda: {})
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<IntegrationSettings {self.integration_type} for User {self.user_id}>'

class SpotifyActivity(db.Model):
    __tablename__ = 'spotify_activity'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('roboto_users.id'), nullable=False)
    
    track_name: Mapped[str] = mapped_column(String(200), nullable=True)
    artist_name: Mapped[str] = mapped_column(String(200), nullable=True)
    album_name: Mapped[str] = mapped_column(String(200), nullable=True)
    track_uri: Mapped[str] = mapped_column(String(200), nullable=True)
    
    played_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    
    activity_data = db.Column(db.JSON, default=lambda: {})
    
    def __repr__(self):
        return f'<SpotifyActivity {self.track_name} by {self.artist_name}>'

class OAuth(db.Model):
    __tablename__ = 'oauth_tokens'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    browser_session_key: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    token = db.Column(db.JSON, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OAuth {self.provider} for User {self.user_id}>'

# Create tables function
def create_tables():
    """Create all database tables"""
    db.create_all()
    print("Database tables created successfully")
    print("Tables created: User, UserData, ConversationSession, MemoryEntry, IntegrationSettings, SpotifyActivity, OAuth")

if __name__ == '__main__':
    # For testing - create tables if run directly
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roboto_test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        create_tables()