"""
Pomodoro Session Service
Handles business logic for Pomodoro sessions
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.models.pomodoro_session import PomodoroSessionModel
from app import db
from app.utils.exceptions import ValidationException

class PomodoroSessionService:
    """Service layer for Pomodoro session management"""

    def create_session(self, user_id: str, session_type: str, duration: int, task: Optional[str] = None) -> PomodoroSessionModel:
        """Create a new Pomodoro session"""
        if not user_id:
            raise ValidationException("User ID is required")
        
        if session_type not in ['focus', 'short_break', 'long_break']:
            raise ValidationException("Invalid session type")
        
        if duration <= 0:
            raise ValidationException("Duration must be positive")

        session = PomodoroSessionModel(
            user_id=user_id,
            session_type=session_type,
            duration=duration,
            start_time=datetime.utcnow(),
            task=task
        )

        db.session.add(session)
        db.session.commit()
        
        return session

    def get_session(self, session_id: str) -> Optional[PomodoroSessionModel]:
        """Get a specific session by ID"""
        return PomodoroSessionModel.query.get(session_id)

    def get_user_sessions(self, user_id: str) -> List[PomodoroSessionModel]:
        """Get all sessions for a user"""
        return PomodoroSessionModel.query.filter_by(user_id=user_id).all()

    def update_session(self, session_id: str, data: Dict) -> Optional[PomodoroSessionModel]:
        """Update a session"""
        session = self.get_session(session_id)
        if not session:
            return None

        # Update allowed fields
        if 'actual_duration' in data:
            session.actual_duration = data['actual_duration']
        if 'end_time' in data:
            session.end_time = data['end_time']
        if 'status' in data:
            session.status = data['status']
        if 'productivity_score' in data:
            session.productivity_score = data['productivity_score']
        if 'task' in data:
            session.task = data['task']

        db.session.commit()
        return session

    def end_session(self, session_id: str, status: str = 'completed') -> Optional[PomodoroSessionModel]:
        """End a Pomodoro session"""
        session = self.get_session(session_id)
        if not session:
            return None

        session.end_time = datetime.utcnow()
        session.status = status
        if session.start_time:
            session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)

        db.session.commit()
        return session

    def get_active_session(self, user_id: str) -> Optional[PomodoroSessionModel]:
        """Get user's active session if exists"""
        return PomodoroSessionModel.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

    def interrupt_session(self, session_id: str) -> Optional[PomodoroSessionModel]:
        """Mark a session as interrupted"""
        return self.end_session(session_id, status='interrupted')

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        db.session.delete(session)
        db.session.commit()
        return True