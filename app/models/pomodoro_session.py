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
    user_id = db.Column(db.String(36), nullable=False, index=True)  # Just store user_id as string without foreign key
    session_type = db.Column(db.String(20), nullable=False)  # focus, short_break, long_break
    duration = db.Column(db.Integer, nullable=False)         # ระยะเวลาที่ตั้งไว้ (นาที)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    actual_duration = db.Column(db.Integer)                  # ระยะเวลาที่ใช้จริง (นาที)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, completed, interrupted
    is_completed = db.Column(db.Boolean, default=False)
    is_interrupted = db.Column(db.Boolean, default=False)
    interruption_count = db.Column(db.Integer, default=0)
    interruption_reasons = db.Column(db.Text)
    
    # Related entities (removed foreign keys for now)
    lesson_id = db.Column(db.String(36))
    section_id = db.Column(db.String(36))
    task_id = db.Column(db.String(36))
    task = db.Column(db.String(255))  # Store task name directly
    
    # Settings
    auto_start_next = db.Column(db.Boolean, default=True)
    notification_enabled = db.Column(db.Boolean, default=True)
    sound_enabled = db.Column(db.Boolean, default=True)
    
    # Session feedback
    notes = db.Column(db.Text)
    productivity_score = db.Column(db.Integer)
    mood_before = db.Column(db.String(50))
    mood_after = db.Column(db.String(50))
    focus_score = db.Column(db.Integer)
    energy_level = db.Column(db.Integer)
    difficulty_level = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<PomodoroSessionModel {self.id} {self.session_type}>'

    def to_dict(self):
        """Convert model to dictionary."""
        # Get task title if task_id exists
        task_title = None
        if self.task_id:
            from app.models.task import TaskModel
            task = TaskModel.query.get(self.task_id)
            if task:
                task_title = task.title
                
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'duration': self.duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'actual_duration': self.actual_duration,
            'status': self.status,
            'is_completed': self.is_completed,
            'is_interrupted': self.is_interrupted,
            'interruption_count': self.interruption_count,
            'interruption_reasons': self.interruption_reasons,
            'lesson_id': self.lesson_id,
            'section_id': self.section_id,
            'task_id': self.task_id,
            'task': task_title,  # Include task title in response
            'auto_start_next': self.auto_start_next,
            'notification_enabled': self.notification_enabled,
            'sound_enabled': self.sound_enabled,
            'notes': self.notes,
            'productivity_score': self.productivity_score,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'focus_score': self.focus_score,
            'energy_level': self.energy_level,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }