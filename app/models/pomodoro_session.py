"""
Pomodoro Session Model
Handles persistence of Pomodoro session data
"""

from app import db
from datetime import datetime
import uuid

class PomodoroSessionModel(db.Model):
    """
    SQLAlchemy model for PomodoroSession entity.
    Maps domain entity to database table.
    """
    __tablename__ = 'pomodoro_session'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    session_type = db.Column(db.String(20), nullable=False)  # focus, short_break, long_break
    duration = db.Column(db.Integer, nullable=False)         # ระยะเวลาที่ตั้งไว้ (นาที)
    actual_duration = db.Column(db.Integer)                  # ระยะเวลาที่ใช้จริง (นาที)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, completed, interrupted
    productivity_score = db.Column(db.Integer)
    task = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<PomodoroSessionModel {self.id} {self.session_type}>'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'duration': self.duration,
            'actual_duration': self.actual_duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'productivity_score': self.productivity_score,
            'task': self.task,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }