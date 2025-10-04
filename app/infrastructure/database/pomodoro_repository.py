"""
Pomodoro Repository Implementation
Database implementation for Pomodoro session operations
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from app import db
from app.domain.entities.pomodoro_session import PomodoroSession, SessionType, SessionStatus
from app.domain.interfaces.pomodoro_repository import PomodoroRepository

class PomodoroRepositoryImpl(PomodoroRepository):
    """Database implementation of Pomodoro repository"""
    
    def __init__(self, database):
        self.db = database
    
    def create_session(self, session: PomodoroSession) -> PomodoroSession:
        """Create a new pomodoro session"""
        try:
            query = text("""
                INSERT INTO pomodoro_session (
                    id, user_id, session_type, duration, start_time, end_time,
                    actual_duration, status, is_completed, is_interrupted,
                    interruption_count, interruption_reasons, lesson_id,
                    section_id, task_id, auto_start_next, notification_enabled,
                    sound_enabled, notes, productivity_score, mood_before,
                    mood_after, focus_score, energy_level, difficulty_level,
                    created_at, updated_at
                ) VALUES (
                    :id, :user_id, :session_type, :duration, :start_time, :end_time,
                    :actual_duration, :status, :is_completed, :is_interrupted,
                    :interruption_count, :interruption_reasons, :lesson_id,
                    :section_id, :task_id, :auto_start_next, :notification_enabled,
                    :sound_enabled, :notes, :productivity_score, :mood_before,
                    :mood_after, :focus_score, :energy_level, :difficulty_level,
                    :created_at, :updated_at
                )
            """)
            
            self.db.session.execute(query, {
                'id': session.id,
                'user_id': session.user_id,
                'session_type': session.session_type.value,
                'duration': session.duration,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'actual_duration': session.actual_duration,
                'status': session.status.value,
                'is_completed': session.is_completed,
                'is_interrupted': session.is_interrupted,
                'interruption_count': session.interruption_count,
                'interruption_reasons': str(session.interruption_reasons) if session.interruption_reasons else None,
                'lesson_id': session.lesson_id,
                'section_id': session.section_id,
                'task_id': session.task_id,
                'auto_start_next': session.auto_start_next,
                'notification_enabled': session.notification_enabled,
                'sound_enabled': session.sound_enabled,
                'notes': session.notes,
                'productivity_score': session.productivity_score,
                'mood_before': session.mood_before,
                'mood_after': session.mood_after,
                'focus_score': session.focus_score,
                'energy_level': session.energy_level,
                'difficulty_level': session.difficulty_level,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })
            
            self.db.session.commit()
            return session
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_session_by_id(self, session_id: str, user_id: str) -> Optional[PomodoroSession]:
        """Get session by ID"""
        try:
            query = text("""
                SELECT * FROM pomodoro_session 
                WHERE id = :session_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'session_id': session_id,
                'user_id': user_id
            }).fetchone()
            
            if result:
                return self._row_to_session(result)
            return None
            
        except Exception as e:
            raise e
    
    def get_active_session(self, user_id: str) -> Optional[PomodoroSession]:
        """Get currently active session for user"""
        try:
            query = text("""
                SELECT * FROM pomodoro_session 
                WHERE user_id = :user_id AND status = 'active'
                ORDER BY start_time DESC
                LIMIT 1
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id
            }).fetchone()
            
            if result:
                return self._row_to_session(result)
            return None
            
        except Exception as e:
            raise e
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[PomodoroSession]:
        """Get user's pomodoro sessions"""
        try:
            query = text("""
                SELECT * FROM pomodoro_session 
                WHERE user_id = :user_id
                ORDER BY start_time DESC
                LIMIT :limit
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id,
                'limit': limit
            }).fetchall()
            
            return [self._row_to_session(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_sessions_by_type(self, user_id: str, session_type: SessionType) -> List[PomodoroSession]:
        """Get sessions by type"""
        try:
            query = text("""
                SELECT * FROM pomodoro_session 
                WHERE user_id = :user_id AND session_type = :session_type
                ORDER BY start_time DESC
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id,
                'session_type': session_type.value
            }).fetchall()
            
            return [self._row_to_session(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_sessions_by_date_range(self, user_id: str, start_date: datetime, end_date: datetime) -> List[PomodoroSession]:
        """Get sessions within date range"""
        try:
            query = text("""
                SELECT * FROM pomodoro_session 
                WHERE user_id = :user_id 
                AND start_time >= :start_date 
                AND start_time <= :end_date
                ORDER BY start_time DESC
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }).fetchall()
            
            return [self._row_to_session(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_lesson_sessions(self, user_id: str, lesson_id: str) -> List[PomodoroSession]:
        """Get sessions for a specific lesson"""
        try:
            query = text("""
                SELECT * FROM pomodoro_session 
                WHERE user_id = :user_id AND lesson_id = :lesson_id
                ORDER BY start_time DESC
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id,
                'lesson_id': lesson_id
            }).fetchall()
            
            return [self._row_to_session(row) for row in result]
            
        except Exception as e:
            raise e
    
    def update_session(self, session: PomodoroSession) -> PomodoroSession:
        """Update session"""
        try:
            query = text("""
                UPDATE pomodoro_session SET
                    session_type = :session_type,
                    duration = :duration,
                    start_time = :start_time,
                    end_time = :end_time,
                    actual_duration = :actual_duration,
                    status = :status,
                    is_completed = :is_completed,
                    is_interrupted = :is_interrupted,
                    interruption_count = :interruption_count,
                    interruption_reasons = :interruption_reasons,
                    lesson_id = :lesson_id,
                    section_id = :section_id,
                    task_id = :task_id,
                    notes = :notes,
                    productivity_score = :productivity_score,
                    mood_before = :mood_before,
                    mood_after = :mood_after,
                    focus_score = :focus_score,
                    energy_level = :energy_level,
                    difficulty_level = :difficulty_level,
                    updated_at = :updated_at
                WHERE id = :id AND user_id = :user_id
            """)
            
            self.db.session.execute(query, {
                'id': session.id,
                'user_id': session.user_id,
                'session_type': session.session_type.value,
                'duration': session.duration,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'actual_duration': session.actual_duration,
                'status': session.status.value,
                'is_completed': session.is_completed,
                'is_interrupted': session.is_interrupted,
                'interruption_count': session.interruption_count,
                'interruption_reasons': str(session.interruption_reasons) if session.interruption_reasons else None,
                'lesson_id': session.lesson_id,
                'section_id': session.section_id,
                'task_id': session.task_id,
                'notes': session.notes,
                'productivity_score': session.productivity_score,
                'mood_before': session.mood_before,
                'mood_after': session.mood_after,
                'focus_score': session.focus_score,
                'energy_level': session.energy_level,
                'difficulty_level': session.difficulty_level,
                'updated_at': session.updated_at.isoformat()
            })
            
            self.db.session.commit()
            return session
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete session"""
        try:
            query = text("""
                DELETE FROM pomodoro_session 
                WHERE id = :session_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'session_id': session_id,
                'user_id': user_id
            })
            
            self.db.session.commit()
            return result.rowcount > 0
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_session_statistics(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> dict:
        """Get session statistics"""
        try:
            # Default to last 30 days if no date range provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            query = text("""
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN session_type = 'focus' THEN 1 END) as focus_sessions,
                    COUNT(CASE WHEN session_type = 'short_break' THEN 1 END) as short_break_sessions,
                    COUNT(CASE WHEN session_type = 'long_break' THEN 1 END) as long_break_sessions,
                    COUNT(CASE WHEN is_completed = 1 THEN 1 END) as completed_sessions,
                    SUM(CASE WHEN session_type = 'focus' THEN duration ELSE 0 END) as total_focus_time,
                    AVG(CASE WHEN session_type = 'focus' THEN productivity_score END) as avg_productivity,
                    AVG(CASE WHEN session_type = 'focus' THEN focus_score END) as avg_focus_score
                FROM pomodoro_session 
                WHERE user_id = :user_id 
                AND start_time >= :start_date 
                AND start_time <= :end_date
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }).fetchone()
            
            return {
                'total_sessions': result.total_sessions or 0,
                'focus_sessions': result.focus_sessions or 0,
                'short_break_sessions': result.short_break_sessions or 0,
                'long_break_sessions': result.long_break_sessions or 0,
                'completed_sessions': result.completed_sessions or 0,
                'total_focus_time': result.total_focus_time or 0,
                'avg_productivity': float(result.avg_productivity) if result.avg_productivity else 0,
                'avg_focus_score': float(result.avg_focus_score) if result.avg_focus_score else 0
            }
            
        except Exception as e:
            raise e
    
    def get_daily_statistics(self, user_id: str, date: datetime) -> dict:
        """Get daily statistics"""
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            return self.get_session_statistics(user_id, start_of_day, end_of_day)
            
        except Exception as e:
            raise e
    
    def get_weekly_statistics(self, user_id: str, week_start: datetime) -> dict:
        """Get weekly statistics"""
        try:
            week_end = week_start + timedelta(days=7)
            return self.get_session_statistics(user_id, week_start, week_end)
            
        except Exception as e:
            raise e
    
    def get_monthly_statistics(self, user_id: str, month: int, year: int) -> dict:
        """Get monthly statistics"""
        try:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            return self.get_session_statistics(user_id, start_date, end_date)
            
        except Exception as e:
            raise e
    
    def _row_to_session(self, row) -> PomodoroSession:
        """Convert database row to PomodoroSession entity"""
        return PomodoroSession(
            id=row.id,
            user_id=row.user_id,
            session_type=SessionType(row.session_type),
            duration=row.duration,
            start_time=datetime.fromisoformat(row.start_time) if row.start_time else None,
            end_time=datetime.fromisoformat(row.end_time) if row.end_time else None,
            actual_duration=row.actual_duration,
            status=SessionStatus(row.status),
            is_completed=bool(row.is_completed),
            is_interrupted=bool(row.is_interrupted),
            interruption_count=row.interruption_count,
            interruption_reasons=eval(row.interruption_reasons) if row.interruption_reasons else [],
            lesson_id=row.lesson_id,
            section_id=row.section_id,
            task_id=row.task_id,
            auto_start_next=bool(row.auto_start_next),
            notification_enabled=bool(row.notification_enabled),
            sound_enabled=bool(row.sound_enabled),
            notes=row.notes,
            productivity_score=row.productivity_score,
            mood_before=row.mood_before,
            mood_after=row.mood_after,
            focus_score=row.focus_score,
            energy_level=row.energy_level,
            difficulty_level=row.difficulty_level,
            created_at=datetime.fromisoformat(row.created_at) if row.created_at else None,
            updated_at=datetime.fromisoformat(row.updated_at) if row.updated_at else None
        )
