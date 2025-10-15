"""
Pomodoro Statistics SQLAlchemy model for database persistence.
Infrastructure layer implementation.
"""

from app.db_instance import db
from datetime import datetime
import uuid

class PomodoroStatisticsModel(db.Model):
    """
    SQLAlchemy model for PomodoroStatistics entity.
    Maps domain entity to database table.
    """
    __tablename__ = 'pomodoro_statistics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    total_sessions = db.Column(db.Integer, default=0)
    total_focus_time = db.Column(db.Integer, default=0)
    total_break_time = db.Column(db.Integer, default=0)
    total_long_break_time = db.Column(db.Integer, default=0)
    total_interrupted_sessions = db.Column(db.Integer, default=0)
    total_completed_sessions = db.Column(db.Integer, default=0)
    total_productivity_score = db.Column(db.Integer, default=0)
    total_tasks_completed = db.Column(db.Integer, default=0)
    total_tasks = db.Column(db.Integer, default=0)
    total_focus_sessions = db.Column(db.Integer, default=0)
    total_short_break_sessions = db.Column(db.Integer, default=0)
    total_long_break_sessions = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)
    total_effective_time = db.Column(db.Integer, default=0)
    total_ineffective_time = db.Column(db.Integer, default=0)
    total_abandoned_sessions = db.Column(db.Integer, default=0)
    total_on_time_sessions = db.Column(db.Integer, default=0)
    total_late_sessions = db.Column(db.Integer, default=0)
    average_session_duration = db.Column(db.Float, default=0.0)
    productivity_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<PomodoroStatisticsModel {self.id} {self.date}>'

    def to_dict(self):
        """
        Convert model to dictionary (MVC pattern).
        
        Returns:
            Dictionary representation of pomodoro statistics
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'total_sessions': self.total_sessions,
            'total_focus_time': self.total_focus_time,
            'total_break_time': self.total_break_time,
            'total_long_break_time': self.total_long_break_time,
            'total_interrupted_sessions': self.total_interrupted_sessions,
            'total_completed_sessions': self.total_completed_sessions,
            'total_productivity_score': self.total_productivity_score,
            'total_tasks_completed': self.total_tasks_completed,
            'total_tasks': self.total_tasks,
            'total_focus_sessions': self.total_focus_sessions,
            'total_short_break_sessions': self.total_short_break_sessions,
            'total_long_break_sessions': self.total_long_break_sessions,
            'total_time_spent': self.total_time_spent,
            'total_effective_time': self.total_effective_time,
            'total_ineffective_time': self.total_ineffective_time,
            'total_abandoned_sessions': self.total_abandoned_sessions,
            'total_on_time_sessions': self.total_on_time_sessions,
            'total_late_sessions': self.total_late_sessions,
            'average_session_duration': self.average_session_duration,
            'productivity_score': self.productivity_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }