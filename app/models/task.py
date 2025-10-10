"""
Task SQLAlchemy model for database persistence.
Infrastructure layer implementation.
"""

from app import db
from datetime import datetime
import uuid
import json


class TaskModel(db.Model):
    """
    SQLAlchemy model for Task entity.
    Maps domain entity to database table.
    """
    __tablename__ = 'task'
    
    # Basic task information
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Task classification
    task_type = db.Column(db.String(20), default='other', nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    priority = db.Column(db.String(10), default='medium', nullable=False, index=True)
    
    # Scheduling
    due_date = db.Column(db.DateTime)
    estimated_duration = db.Column(db.Integer)  # minutes
    
    # Associations
    lesson_id = db.Column(db.String(36), nullable=True, index=True)
    section_id = db.Column(db.String(36), nullable=True, index=True)
    
    # Metadata
    tags = db.Column(db.Text)  # JSON string of tags
    is_reminder_enabled = db.Column(db.Boolean, default=True, nullable=False)
    reminder_time = db.Column(db.Integer)  # minutes before due date
    
    # Progress tracking
    progress_percentage = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, default=0)  # minutes
    completed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<TaskModel {self.title}>'
    
    def to_dict(self):
        """
        Convert model to dictionary (MVC pattern).
        
        Returns:
            Dictionary representation of task
        """
        # Parse tags from JSON
        tags = []
        if self.tags:
            try:
                tags = json.loads(self.tags) if isinstance(self.tags, str) else self.tags
            except (json.JSONDecodeError, TypeError):
                tags = []
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_duration': self.estimated_duration,
            'lesson_id': self.lesson_id,
            'section_id': self.section_id,
            'tags': tags,
            'is_reminder_enabled': self.is_reminder_enabled,
            'reminder_time': self.reminder_time,
            'progress_percentage': self.progress_percentage,
            'time_spent': self.time_spent,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
