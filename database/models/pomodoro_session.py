from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class PomodoroSession(BaseModel):
    """Pomodoro session model for time management"""
    
    # Session identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    session_type = Column(String(20), default='focus', nullable=False, index=True)  # focus, short_break, long_break
    
    # Session timing
    duration = Column(Integer, nullable=False)  # minutes
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, index=True)
    actual_duration = Column(Integer)  # actual time spent in minutes
    
    # Session status
    is_completed = Column(Boolean, default=False, index=True)
    is_interrupted = Column(Boolean, default=False)
    interruption_count = Column(Integer, default=0)
    interruption_reasons = Column(Text)  # JSON string of interruption reasons
    
    # Session context
    lesson_id = Column(String(36), ForeignKey('lesson.id'), index=True)
    section_id = Column(String(36), ForeignKey('lessonsection.id'), index=True)
    task_id = Column(String(36), ForeignKey('task.id'), index=True)
    
    # Session settings
    auto_start_next = Column(Boolean, default=True)  # auto-start next session
    notification_enabled = Column(Boolean, default=True)
    sound_enabled = Column(Boolean, default=True)
    
    # Session notes and feedback
    notes = Column(Text)  # session notes
    productivity_score = Column(Integer)  # 1-10 self-assessment
    mood_before = Column(String(20))  # mood before session
    mood_after = Column(String(20))  # mood after session
    
    # Session statistics
    focus_score = Column(Integer)  # 1-10 focus assessment
    energy_level = Column(Integer)  # 1-10 energy level
    difficulty_level = Column(Integer)  # 1-10 difficulty assessment
    
    # Relationships
    user = relationship('User', back_populates='pomodoro_sessions')
    lesson = relationship('Lesson', back_populates='pomodoro_sessions')
    section = relationship('LessonSection', back_populates='pomodoro_sessions')
    task = relationship('Task')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_pomodoro_user_type', 'user_id', 'session_type'),
        Index('idx_pomodoro_start_time', 'start_time', 'is_completed'),
        Index('idx_pomodoro_lesson_section', 'lesson_id', 'section_id'),
        Index('idx_pomodoro_completion', 'is_completed', 'session_type'),
    )
    
    @property
    def session_status(self):
        """Get current session status"""
        if self.is_completed:
            return 'completed'
        elif self.is_interrupted:
            return 'interrupted'
        elif self.end_time:
            return 'finished'
        else:
            return 'active'
    
    @property
    def efficiency_score(self):
        """Calculate efficiency score based on actual vs planned duration"""
        if self.duration and self.actual_duration:
            if self.actual_duration <= self.duration:
                return 100  # Perfect efficiency
            else:
                # Penalty for going over time
                overage_ratio = (self.actual_duration - self.duration) / self.duration
                penalty = min(overage_ratio * 50, 50)  # Max 50% penalty
                return max(100 - penalty, 0)
        return 0
    
    @property
    def is_active(self):
        """Check if session is currently active"""
        if self.is_completed or self.is_interrupted:
            return False
        if self.start_time and not self.end_time:
            from datetime import datetime
            # Check if session is within reasonable time bounds
            max_duration = self.duration * 2  # Allow 2x duration for breaks
            return (datetime.utcnow() - self.start_time).total_seconds() / 60 <= max_duration
        return False
    
    @property
    def time_remaining(self):
        """Get time remaining in session (minutes)"""
        if self.is_active:
            from datetime import datetime
            elapsed = (datetime.utcnow() - self.start_time).total_seconds() / 60
            remaining = self.duration - elapsed
            return max(0, int(remaining))
        return 0
    
    def __repr__(self):
        return f'<PomodoroSession {self.session_type} ({self.duration}min) - {self.session_status}>'
