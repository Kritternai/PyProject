from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Integer, Numeric, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class ProgressTracking(BaseModel):
    """Progress tracking model for monitoring learning progress"""
    
    # Progress identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False, index=True)
    section_id = Column(String(36), ForeignKey('lessonsection.id'), index=True)  # NULL for lesson-level progress
    
    # Progress type and measurement
    progress_type = Column(String(50), nullable=False, index=True)  # time_spent, completion, quiz_score, assignment_score, attendance
    value = Column(Numeric(10, 2), nullable=False)  # measured value
    max_value = Column(Numeric(10, 2))  # maximum possible value
    percentage = Column(Numeric(5, 2))  # calculated percentage (0-100)
    
    # Progress metadata
    unit = Column(String(20))  # minutes, points, percentage, etc.
    notes = Column(Text)  # additional notes about progress
    confidence_score = Column(Numeric(3, 2))  # 0.0-1.0 for AI-generated progress
    
    # Progress context
    session_id = Column(String(36))  # for grouping related progress records
    study_method = Column(String(50))  # pomodoro, traditional, spaced_repetition
    environment = Column(String(50))  # home, library, classroom, online
    
    # Progress validation
    is_verified = Column(String(20), default=False)  # manually verified progress
    verified_by = Column(String(36), ForeignKey('user.id'), index=True)  # who verified
    verified_at = Column(DateTime)
    
    # Relationships
    user = relationship('User', back_populates='progress_records', foreign_keys=[user_id])
    lesson = relationship('Lesson', back_populates='progress_records', foreign_keys=[lesson_id])
    section = relationship('LessonSection', back_populates='progress_records', foreign_keys=[section_id])
    verifier = relationship('User', foreign_keys=[verified_by])
    
    # Composite indexes
    __table_args__ = (
        Index('idx_progress_user_lesson', 'user_id', 'lesson_id'),
        Index('idx_progress_type_value', 'progress_type', 'value'),
        Index('idx_progress_section_type', 'section_id', 'progress_type'),
        Index('idx_progress_session', 'session_id', 'progress_type'),
        Index('idx_progress_verified', 'is_verified', 'verified_at'),
    )
    
    @property
    def progress_ratio(self):
        """Get progress as ratio (0.0 to 1.0)"""
        if self.max_value and self.max_value > 0:
            return float(self.value / self.max_value)
        return 0.0
    
    @property
    def is_complete(self):
        """Check if progress is complete"""
        if self.max_value:
            return float(self.value) >= float(self.max_value)
        return self.percentage >= 100 if self.percentage else False
    
    @property
    def progress_status(self):
        """Get human-readable progress status"""
        if self.is_complete:
            return 'completed'
        elif self.percentage and self.percentage > 50:
            return 'in_progress'
        elif self.percentage and self.percentage > 0:
            return 'started'
        else:
            return 'not_started'
    
    def __repr__(self):
        return f'<ProgressTracking {self.progress_type}: {self.value}/{self.max_value} ({self.percentage}%)>'
