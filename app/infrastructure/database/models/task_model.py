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
    
    def to_domain_entity(self):
        """
        Convert SQLAlchemy model to domain entity.
        
        Returns:
            Task domain entity
        """
        from app.domain.entities.task import Task, TaskStatus, TaskPriority, TaskType
        
        # Parse tags from JSON
        tags = []
        if self.tags:
            try:
                tags = json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                tags = []
        
        # Convert string values to enums
        task_type = TaskType(self.task_type)
        status = TaskStatus(self.status)
        priority = TaskPriority(self.priority)
        
        # Create domain entity
        return Task(
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            task_type=task_type,
            status=status,
            priority=priority,
            due_date=self.due_date,
            estimated_duration=self.estimated_duration,
            lesson_id=self.lesson_id,
            section_id=self.section_id,
            tags=tags,
            is_reminder_enabled=self.is_reminder_enabled,
            reminder_time=self.reminder_time,
            task_id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_domain_entity(cls, task):
        """
        Create SQLAlchemy model from domain entity.
        
        Args:
            task: Task domain entity
            
        Returns:
            TaskModel instance
        """
        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            task_type=task.task_type.value,
            status=task.status.value,
            priority=task.priority.value,
            due_date=task.due_date,
            estimated_duration=task.estimated_duration,
            lesson_id=task.lesson_id,
            section_id=task.section_id,
            tags=json.dumps(task.tags) if task.tags else None,
            is_reminder_enabled=task.is_reminder_enabled,
            reminder_time=task.reminder_time,
            progress_percentage=task.progress_percentage,
            time_spent=task.time_spent,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
