"""
Pomodoro Session Entity
Domain entity for Pomodoro session management
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

class SessionType(Enum):
    """Pomodoro session types"""
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"

class SessionStatus(Enum):
    """Pomodoro session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"

class PomodoroSession:
    """Pomodoro Session Domain Entity"""
    
    def __init__(self, 
                 id: str,
                 user_id: str,
                 session_type: SessionType,
                 duration: int,
                 start_time: datetime,
                 **kwargs):
        self.id = id
        self.user_id = user_id
        self.session_type = session_type
        self.duration = duration  # in minutes
        self.start_time = start_time
        self.end_time = kwargs.get('end_time')
        self.actual_duration = kwargs.get('actual_duration')
        self.status = SessionStatus(kwargs.get('status', 'active'))
        self.is_completed = kwargs.get('is_completed', False)
        self.is_interrupted = kwargs.get('is_interrupted', False)
        self.interruption_count = kwargs.get('interruption_count', 0)
        self.interruption_reasons = kwargs.get('interruption_reasons', [])
        
        # Context
        self.lesson_id = kwargs.get('lesson_id')
        self.section_id = kwargs.get('section_id')
        self.task_id = kwargs.get('task_id')
        
        # Settings
        self.auto_start_next = kwargs.get('auto_start_next', True)
        self.notification_enabled = kwargs.get('notification_enabled', True)
        self.sound_enabled = kwargs.get('sound_enabled', True)
        
        # Feedback
        self.notes = kwargs.get('notes')
        self.productivity_score = kwargs.get('productivity_score')
        self.mood_before = kwargs.get('mood_before')
        self.mood_after = kwargs.get('mood_after')
        self.focus_score = kwargs.get('focus_score')
        self.energy_level = kwargs.get('energy_level')
        self.difficulty_level = kwargs.get('difficulty_level')
        
        # Timestamps
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())
    
    def pause(self):
        """Pause the session"""
        if self.status == SessionStatus.ACTIVE:
            self.status = SessionStatus.PAUSED
            self.updated_at = datetime.now()
    
    def resume(self):
        """Resume the session"""
        if self.status == SessionStatus.PAUSED:
            self.status = SessionStatus.ACTIVE
            self.updated_at = datetime.now()
    
    def complete(self):
        """Mark session as completed"""
        self.status = SessionStatus.COMPLETED
        self.is_completed = True
        self.end_time = datetime.now()
        self.actual_duration = self._calculate_actual_duration()
        self.updated_at = datetime.now()
    
    def interrupt(self, reason: str = None):
        """Interrupt the session"""
        self.status = SessionStatus.INTERRUPTED
        self.is_interrupted = True
        self.interruption_count += 1
        if reason:
            if not self.interruption_reasons:
                self.interruption_reasons = []
            self.interruption_reasons.append(reason)
        self.updated_at = datetime.now()
    
    def cancel(self):
        """Cancel the session"""
        self.status = SessionStatus.CANCELLED
        self.end_time = datetime.now()
        self.updated_at = datetime.now()
    
    def _calculate_actual_duration(self) -> int:
        """Calculate actual duration in minutes"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0
    
    @property
    def time_remaining(self) -> int:
        """Get time remaining in minutes"""
        if self.status == SessionStatus.ACTIVE and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            remaining = self.duration - elapsed
            return max(0, int(remaining))
        return 0
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.status == SessionStatus.ACTIVE
    
    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency score (0-100)"""
        if self.actual_duration and self.duration:
            if self.actual_duration <= self.duration:
                return 100.0
            else:
                overage_ratio = (self.actual_duration - self.duration) / self.duration
                penalty = min(overage_ratio * 50, 50)
                return max(100 - penalty, 0)
        return 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type.value,
            'duration': self.duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'actual_duration': self.actual_duration,
            'status': self.status.value,
            'is_completed': self.is_completed,
            'is_interrupted': self.is_interrupted,
            'interruption_count': self.interruption_count,
            'interruption_reasons': self.interruption_reasons,
            'lesson_id': self.lesson_id,
            'section_id': self.section_id,
            'task_id': self.task_id,
            'notes': self.notes,
            'productivity_score': self.productivity_score,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'focus_score': self.focus_score,
            'energy_level': self.energy_level,
            'difficulty_level': self.difficulty_level,
            'time_remaining': self.time_remaining,
            'is_active': self.is_active,
            'efficiency_score': self.efficiency_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PomodoroSession {self.session_type.value} ({self.duration}min) - {self.status.value}>'
