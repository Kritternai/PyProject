from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Reminder(BaseModel):
    """Reminder model for notifications and alerts"""
    
    # Reminder identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Reminder timing
    due_date = Column(DateTime, nullable=False, index=True)
    reminder_time = Column(DateTime, index=True)  # when to send reminder
    start_date = Column(DateTime)  # when reminder becomes active
    
    # Reminder type and settings
    reminder_type = Column(String(20), default='due_date', index=True)  # due_date, custom, recurring, milestone
    is_recurring = Column(Boolean, default=False, index=True)
    recurrence_pattern = Column(String(50))  # daily, weekly, monthly, yearly, custom
    recurrence_interval = Column(Integer, default=1)  # every X days/weeks/months
    recurrence_end_date = Column(DateTime)  # when to stop recurring
    
    # Reminder status
    is_completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime)
    is_dismissed = Column(Boolean, default=False)
    dismissed_at = Column(DateTime)
    
    # Reminder priority and categorization
    priority = Column(String(20), default='medium', index=True)  # low, medium, high, urgent
    category = Column(String(100))  # study, personal, work, health
    tags = Column(Text)  # JSON string of tags
    
    # Reminder relationships
    lesson_id = Column(String(36), ForeignKey('lesson.id'), index=True)
    section_id = Column(String(36), ForeignKey('lessonsection.id'), index=True)
    task_id = Column(String(36), ForeignKey('task.id'), index=True)
    note_id = Column(String(36), ForeignKey('note.id'), index=True)
    
    # Notification settings
    notification_methods = Column(Text)  # JSON string: ['email', 'push', 'sms', 'in_app']
    notification_timing = Column(String(20), default='on_time')  # on_time, 15min_before, 1hour_before, 1day_before
    sound_enabled = Column(Boolean, default=True)
    vibration_enabled = Column(Boolean, default=True)
    
    # Reminder metadata
    external_id = Column(String(100))  # ID from external calendar
    external_url = Column(String(500))  # URL to external calendar
    source_platform = Column(String(50))  # google_calendar, outlook, apple_calendar
    
    # Relationships
    user = relationship('User', back_populates='reminders')
    lesson = relationship('Lesson', back_populates='reminders')
    section = relationship('LessonSection', back_populates='reminders')
    task = relationship('Task', back_populates='reminders')
    note = relationship('Note')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_reminder_user_due', 'user_id', 'due_date'),
        Index('idx_reminder_user_status', 'user_id', 'is_completed'),
        Index('idx_reminder_priority_due', 'priority', 'due_date'),
        Index('idx_reminder_recurring', 'is_recurring', 'due_date'),
        Index('idx_reminder_lesson_task', 'lesson_id', 'task_id'),
    )
    
    @property
    def is_overdue(self):
        """Check if reminder is overdue"""
        if self.due_date and not self.is_completed:
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def is_active(self):
        """Check if reminder is currently active"""
        if self.is_completed or self.is_dismissed:
            return False
        
        from datetime import datetime
        now = datetime.utcnow()
        
        # Check start date
        if self.start_date and now < self.start_date:
            return False
        
        # Check end date for recurring reminders
        if self.is_recurring and self.recurrence_end_date and now > self.recurrence_end_date:
            return False
        
        return True
    
    @property
    def next_occurrence(self):
        """Get next occurrence for recurring reminders"""
        if not self.is_recurring:
            return self.due_date
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        if self.recurrence_end_date and now > self.recurrence_end_date:
            return None
        
        # Calculate next occurrence based on pattern
        current_date = self.due_date
        while current_date <= now:
            if self.recurrence_pattern == 'daily':
                current_date += timedelta(days=self.recurrence_interval)
            elif self.recurrence_pattern == 'weekly':
                current_date += timedelta(weeks=self.recurrence_interval)
            elif self.recurrence_pattern == 'monthly':
                # Simple monthly increment (not perfect for all months)
                current_date += timedelta(days=30 * self.recurrence_interval)
            elif self.recurrence_pattern == 'yearly':
                current_date += timedelta(days=365 * self.recurrence_interval)
        
        return current_date
    
    @property
    def urgency_level(self):
        """Get urgency level based on due date and priority"""
        if self.is_completed:
            return 'completed'
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        if self.due_date:
            time_until_due = self.due_date - now
            
            if time_until_due < timedelta(hours=1):
                return 'critical'
            elif time_until_due < timedelta(hours=24):
                return 'urgent'
            elif time_until_due < timedelta(days=3):
                return 'high'
            elif time_until_due < timedelta(days=7):
                return 'medium'
            else:
                return 'low'
        
        return 'medium'
    
    def __repr__(self):
        return f'<Reminder {self.title} - {self.reminder_type} ({self.priority})>'
