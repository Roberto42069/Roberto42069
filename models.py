from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from flask_login import UserMixin
from app_enhanced import db

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class RobotoUser(UserMixin, db.Model):
    """Legacy Roboto user model for compatibility"""
    __tablename__ = 'roboto_users'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    replit_user_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    replit_user_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship to user data
    user_data = db.relationship('UserData', back_populates='user', uselist=False, cascade='all, delete-orphan')

    @property
    def roboto_data(self):
        """Alias for backward compatibility"""
        return self.user_data

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
    __tablename__ = 'user_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'), nullable=False)

    # Roboto conversation data
    chat_history = db.Column(JSON, default=lambda: [])
    learned_patterns = db.Column(JSON, default=lambda: {})
    user_preferences = db.Column(JSON, default=lambda: {})
    emotional_history = db.Column(JSON, default=lambda: [])
    memory_system_data = db.Column(JSON, default=lambda: {})

    # Current state
    current_emotion: Mapped[str] = mapped_column(String(50), default='curious')
    current_user_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # Custom personality (max 3000 characters, permanent)
    custom_personality: Mapped[str] = mapped_column(Text, nullable=True)

    # Metadata with different names to avoid conflict
    data_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = db.relationship('User', back_populates='user_data')

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

class RateLimitTracker(db.Model):
    __tablename__ = 'rate_limit_tracker'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'<RateLimitTracker {self.identifier}:{self.endpoint}>'

class SecurityAuditLog(db.Model):
    __tablename__ = 'security_audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)
    details = db.Column(db.JSON, default=lambda: {})
    risk_level: Mapped[str] = mapped_column(String(20), default='low')
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SecurityAuditLog {self.event_type} - {self.risk_level}>'

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    session_token: Mapped[str] = mapped_column(String(256), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f'<UserSession {self.id} for User {self.user_id}>'

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