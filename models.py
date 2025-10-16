from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from flask_login import UserMixin

# db will be initialized by app.py
db = None

class RobotoUser(UserMixin, db.Model):
    """Legacy Roboto user model for compatibility"""
    __tablename__ = 'roboto_users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    settings: Mapped[dict] = mapped_column(JSON, nullable=True)
    profile_text: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f'<RobotoUser {self.username}>'