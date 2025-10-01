from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Lesson(BaseModel):
    """Lesson model for managing learning content"""
    
    # Basic lesson information
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Lesson status and progress
    status = Column(String(50), default='not_started', nullable=False, index=True)  # not_started, in_progress, completed, archived
    progress_percentage = Column(Integer, default=0)  # 0-100
    
    # Lesson metadata
    difficulty_level = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    estimated_duration = Column(Integer)  # minutes
    color_theme = Column(Integer, default=1)  # 1-6 color themes
    is_favorite = Column(Boolean, default=False, index=True)
    
    # External platform integration
    source_platform = Column(String(50), default='manual', index=True)  # manual, google_classroom, ms_teams, canvas
    external_id = Column(String(100), index=True)  # ID from external platform
    external_url = Column(String(500))  # URL to external platform
    
    # Lesson content
    tags = Column(Text)  # JSON string of tags
    author_name = Column(String(100))
    subject = Column(String(100))
    grade_level = Column(String(20))
    
    # Statistics
    total_sections = Column(Integer, default=0)
    completed_sections = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # minutes
    
    # Relationships
    user = relationship('User', back_populates='lessons')
    sections = relationship('LessonSection', back_populates='lesson', cascade='all, delete-orphan', order_by='LessonSection.order_index')
    notes = relationship('Note', back_populates='lesson', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='lesson', cascade='all, delete-orphan')
    files = relationship('Files', back_populates='lesson', cascade='all, delete-orphan')
    tags = relationship('LessonTag', back_populates='lesson', cascade='all, delete-orphan')
    progress_records = relationship('ProgressTracking', back_populates='lesson', cascade='all, delete-orphan')
    pomodoro_sessions = relationship('PomodoroSession', back_populates='lesson', cascade='all, delete-orphan')
    reminders = relationship('Reminder', back_populates='lesson', cascade='all, delete-orphan')
    
    # Composite indexes for better performance
    __table_args__ = (
        Index('idx_lesson_user_status', 'user_id', 'status'),
        Index('idx_lesson_platform_external', 'source_platform', 'external_id'),
        Index('idx_lesson_user_favorite', 'user_id', 'is_favorite'),
        Index('idx_lesson_user_progress', 'user_id', 'progress_percentage'),
    )
    
    @property
    def is_completed(self):
        """Check if lesson is completed"""
        return self.status == 'completed'
    
    @property
    def progress_ratio(self):
        """Get progress as ratio (0.0 to 1.0)"""
        return self.progress_percentage / 100.0
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class LessonSection(BaseModel):
    """Lesson section model for organizing lesson content"""
    
    # Section identification
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    
    # Section type and organization
    section_type = Column(String(50), nullable=False, index=True)  # text, file, assignment, note, material, quiz, video
    order_index = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default='pending', index=True)  # pending, in_progress, completed, skipped
    
    # Section metadata
    tags = Column(Text)  # JSON string of tags
    due_date = Column(DateTime)
    estimated_duration = Column(Integer)  # minutes
    points = Column(Integer, default=0)  # points for assignments/quizzes
    
    # Progress tracking
    time_spent = Column(Integer, default=0)  # minutes
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # External content
    external_url = Column(String(500))
    external_id = Column(String(100))
    
    # Relationships
    lesson = relationship('Lesson', back_populates='sections')
    notes = relationship('Note', back_populates='section', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='section', cascade='all, delete-orphan')
    files = relationship('Files', back_populates='section', cascade='all, delete-orphan')
    progress_records = relationship('ProgressTracking', back_populates='section', cascade='all, delete-orphan')
    pomodoro_sessions = relationship('PomodoroSession', back_populates='section', cascade='all, delete-orphan')
    reminders = relationship('Reminder', back_populates='section', cascade='all, delete-orphan')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_section_lesson_order', 'lesson_id', 'order_index'),
        Index('idx_section_type_status', 'section_type', 'status'),
        Index('idx_section_due_date', 'due_date'),
    )
    
    @property
    def is_completed(self):
        """Check if section is completed"""
        return self.status == 'completed'
    
    @property
    def is_overdue(self):
        """Check if section is overdue"""
        if self.due_date:
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False
    
    def __repr__(self):
        return f'<LessonSection {self.title} ({self.section_type})>'
