"""
Pomodoro Repository Interface
Abstract interface for Pomodoro session data access
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.entities.pomodoro_session import PomodoroSession, SessionType, SessionStatus

class PomodoroRepository(ABC):
    """Abstract repository for Pomodoro session operations"""
    
    @abstractmethod
    def create_session(self, session: PomodoroSession) -> PomodoroSession:
        """Create a new pomodoro session"""
        pass
    
    @abstractmethod
    def get_session_by_id(self, session_id: str, user_id: str) -> Optional[PomodoroSession]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def get_active_session(self, user_id: str) -> Optional[PomodoroSession]:
        """Get currently active session for user"""
        pass
    
    @abstractmethod
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[PomodoroSession]:
        """Get user's pomodoro sessions"""
        pass
    
    @abstractmethod
    def get_sessions_by_type(self, user_id: str, session_type: SessionType) -> List[PomodoroSession]:
        """Get sessions by type"""
        pass
    
    @abstractmethod
    def get_sessions_by_date_range(self, user_id: str, start_date: datetime, end_date: datetime) -> List[PomodoroSession]:
        """Get sessions within date range"""
        pass
    
    @abstractmethod
    def get_lesson_sessions(self, user_id: str, lesson_id: str) -> List[PomodoroSession]:
        """Get sessions for a specific lesson"""
        pass
    
    @abstractmethod
    def update_session(self, session: PomodoroSession) -> PomodoroSession:
        """Update session"""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete session"""
        pass
    
    @abstractmethod
    def get_session_statistics(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Get session statistics"""
        pass
    
    @abstractmethod
    def get_daily_statistics(self, user_id: str, date: datetime) -> dict:
        """Get daily statistics"""
        pass
    
    @abstractmethod
    def get_weekly_statistics(self, user_id: str, week_start: datetime) -> dict:
        """Get weekly statistics"""
        pass
    
    @abstractmethod
    def get_monthly_statistics(self, user_id: str, month: int, year: int) -> dict:
        """Get monthly statistics"""
        pass
