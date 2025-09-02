from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Task(BaseModel):
    """Task model for task management system"""
    
    # Task identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Task categorization
    task_type = Column(String(50), default='general', index=True)  # general, assignment, study, personal, work
    category = Column(String(100))  # homework, exam, project, etc.
    tags = Column(Text)  # JSON string of tags
    
    # Task status and priority
    status = Column(String(20), default='pending', nullable=False, index=True)  # pending, in_progress, completed, cancelled, overdue
    priority = Column(String(20), default='medium', index=True)  # low, medium, high, urgent
    
    # Task scheduling
    due_date = Column(DateTime, index=True)
    start_date = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Task estimation and tracking
    estimated_time = Column(Integer)  # minutes
    actual_time = Column(Integer, default=0)  # minutes
    progress_percentage = Column(Integer, default=0)  # 0-100
    
    # Task relationships
    lesson_id = Column(String(36), ForeignKey('lesson.id'), index=True)
    section_id = Column(String(36), ForeignKey('lessonsection.id'), index=True)
    parent_task_id = Column(String(36), ForeignKey('task.id'), index=True)  # for subtasks
    
    # Task settings
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly, custom
    reminder_enabled = Column(Boolean, default=True)
    
    # External integration
    external_id = Column(String(100))  # ID from external platform
    external_url = Column(String(500))
    source_platform = Column(String(50))  # google_classroom, ms_teams, etc.
    
    # Statistics
    subtask_count = Column(Integer, default=0)
    completed_subtasks = Column(Integer, default=0)
    
    # Relationships
    user = relationship('User', back_populates='tasks')
    lesson = relationship('Lesson', back_populates='tasks')
    section = relationship('LessonSection', back_populates='tasks')
    parent_task = relationship('Task', remote_side='Task.id', backref='subtasks')
    files = relationship('Files', back_populates='task', cascade='all, delete-orphan')
    reminders = relationship('Reminder', back_populates='task', cascade='all, delete-orphan')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_task_user_status', 'user_id', 'status'),
        Index('idx_task_user_priority', 'user_id', 'priority'),
        Index('idx_task_due_date', 'due_date'),
        Index('idx_task_lesson_section', 'lesson_id', 'section_id'),
        Index('idx_task_status_priority', 'status', 'priority'),
    )
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == 'completed'
    
    @property
    def has_subtasks(self):
        """Check if task has subtasks"""
        return self.subtask_count > 0
    
    @property
    def completion_ratio(self):
        """Get completion ratio (0.0 to 1.0)"""
        return self.progress_percentage / 100.0
    
    def __repr__(self):
        return f'<Task {self.title} ({self.status})>'
