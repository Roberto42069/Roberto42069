from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    profile_image = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationship to user data
    roboto_data = db.relationship('UserData', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

class UserData(db.Model):
    __tablename__ = 'user_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Chat and conversation data
    chat_history = db.Column(db.JSON, default=list)
    learned_patterns = db.Column(db.JSON, default=dict)
    user_preferences = db.Column(db.JSON, default=dict)
    emotional_history = db.Column(db.JSON, default=list)

    # Memory system data
    memory_system_data = db.Column(db.JSON, default=dict)

    # Current state
    current_emotion = db.Column(db.String(50), default='curious')
    current_user_name = db.Column(db.String(100), nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserData {self.user_id}>'

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
    metadata = db.Column(db.JSON, default=dict)

    def __repr__(self):
        return f'<MemoryEntry {self.memory_id}>'

# Create tables function
def create_tables():
    """Create all database tables"""
    db.create_all()
    print("Database tables created successfully")

if __name__ == '__main__':
    # For testing - create tables if run directly
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roboto_test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        create_tables()