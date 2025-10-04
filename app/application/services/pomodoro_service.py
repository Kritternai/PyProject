"""
Pomodoro Service
Business logic for Pomodoro session management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from app.domain.entities.pomodoro_session import PomodoroSession, SessionType, SessionStatus
from app.domain.interfaces.pomodoro_repository import PomodoroRepository

class PomodoroService:
    """Pomodoro session business logic service"""
    
    def __init__(self, pomodoro_repository: PomodoroRepository):
        self.pomodoro_repository = pomodoro_repository
    
    def start_session(self, user_id: str, session_type: SessionType, duration: int, **kwargs) -> PomodoroSession:
        """Start a new pomodoro session"""
        try:
            # Check if user has active session
            active_session = self.pomodoro_repository.get_active_session(user_id)
            if active_session:
                raise ValueError("User already has an active session")
            
            # Create new session
            session = PomodoroSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_type=session_type,
                duration=duration,
                start_time=datetime.now(),
                lesson_id=kwargs.get('lesson_id'),
                section_id=kwargs.get('section_id'),
                task_id=kwargs.get('task_id'),
                notes=kwargs.get('notes'),
                mood_before=kwargs.get('mood_before'),
                auto_start_next=kwargs.get('auto_start_next', True),
                notification_enabled=kwargs.get('notification_enabled', True),
                sound_enabled=kwargs.get('sound_enabled', True)
            )
            
            return self.pomodoro_repository.create_session(session)
            
        except Exception as e:
            raise e
    
    def pause_session(self, user_id: str, session_id: str) -> PomodoroSession:
        """Pause an active session"""
        try:
            session = self.pomodoro_repository.get_session_by_id(session_id, user_id)
            if not session:
                raise ValueError("Session not found")
            
            if not session.is_active:
                raise ValueError("Session is not active")
            
            session.pause()
            return self.pomodoro_repository.update_session(session)
            
        except Exception as e:
            raise e
    
    def resume_session(self, user_id: str, session_id: str) -> PomodoroSession:
        """Resume a paused session"""
        try:
            session = self.pomodoro_repository.get_session_by_id(session_id, user_id)
            if not session:
                raise ValueError("Session not found")
            
            if session.status != SessionStatus.PAUSED:
                raise ValueError("Session is not paused")
            
            session.resume()
            return self.pomodoro_repository.update_session(session)
            
        except Exception as e:
            raise e
    
    def complete_session(self, user_id: str, session_id: str, **kwargs) -> PomodoroSession:
        """Complete a session"""
        try:
            session = self.pomodoro_repository.get_session_by_id(session_id, user_id)
            if not session:
                raise ValueError("Session not found")
            
            # Update feedback if provided
            if 'productivity_score' in kwargs:
                session.productivity_score = kwargs['productivity_score']
            if 'mood_after' in kwargs:
                session.mood_after = kwargs['mood_after']
            if 'focus_score' in kwargs:
                session.focus_score = kwargs['focus_score']
            if 'energy_level' in kwargs:
                session.energy_level = kwargs['energy_level']
            if 'difficulty_level' in kwargs:
                session.difficulty_level = kwargs['difficulty_level']
            if 'notes' in kwargs:
                session.notes = kwargs['notes']
            
            session.complete()
            return self.pomodoro_repository.update_session(session)
            
        except Exception as e:
            raise e
    
    def interrupt_session(self, user_id: str, session_id: str, reason: str = None) -> PomodoroSession:
        """Interrupt a session"""
        try:
            session = self.pomodoro_repository.get_session_by_id(session_id, user_id)
            if not session:
                raise ValueError("Session not found")
            
            if not session.is_active:
                raise ValueError("Session is not active")
            
            session.interrupt(reason)
            return self.pomodoro_repository.update_session(session)
            
        except Exception as e:
            raise e
    
    def cancel_session(self, user_id: str, session_id: str) -> PomodoroSession:
        """Cancel a session"""
        try:
            session = self.pomodoro_repository.get_session_by_id(session_id, user_id)
            if not session:
                raise ValueError("Session not found")
            
            session.cancel()
            return self.pomodoro_repository.update_session(session)
            
        except Exception as e:
            raise e
    
    def get_active_session(self, user_id: str) -> Optional[PomodoroSession]:
        """Get user's active session"""
        return self.pomodoro_repository.get_active_session(user_id)
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[PomodoroSession]:
        """Get user's sessions"""
        return self.pomodoro_repository.get_user_sessions(user_id, limit)
    
    def get_lesson_sessions(self, user_id: str, lesson_id: str) -> List[PomodoroSession]:
        """Get sessions for a lesson"""
        return self.pomodoro_repository.get_lesson_sessions(user_id, lesson_id)
    
    def get_session_statistics(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get session statistics"""
        return self.pomodoro_repository.get_session_statistics(user_id, start_date, end_date)
    
    def get_daily_statistics(self, user_id: str, date: datetime = None) -> Dict[str, Any]:
        """Get daily statistics"""
        if not date:
            date = datetime.now()
        return self.pomodoro_repository.get_daily_statistics(user_id, date)
    
    def get_weekly_statistics(self, user_id: str, week_start: datetime = None) -> Dict[str, Any]:
        """Get weekly statistics"""
        if not week_start:
            # Get start of current week (Monday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return self.pomodoro_repository.get_weekly_statistics(user_id, week_start)
    
    def get_monthly_statistics(self, user_id: str, month: int = None, year: int = None) -> Dict[str, Any]:
        """Get monthly statistics"""
        if not month:
            month = datetime.now().month
        if not year:
            year = datetime.now().year
        
        return self.pomodoro_repository.get_monthly_statistics(user_id, month, year)
    
    def get_productivity_insights(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get productivity insights"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            stats = self.get_session_statistics(user_id, start_date, end_date)
            sessions = self.pomodoro_repository.get_sessions_by_date_range(user_id, start_date, end_date)
            
            # Calculate insights
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.is_completed])
            completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            focus_sessions = [s for s in sessions if s.session_type == SessionType.FOCUS]
            avg_productivity = sum([s.productivity_score for s in focus_sessions if s.productivity_score]) / len([s for s in focus_sessions if s.productivity_score]) if focus_sessions else 0
            
            best_time_of_day = self._get_best_time_of_day(sessions)
            most_productive_day = self._get_most_productive_day(sessions)
            
            return {
                'completion_rate': round(completion_rate, 2),
                'avg_productivity': round(avg_productivity, 2),
                'total_focus_time': stats['total_focus_time'],
                'best_time_of_day': best_time_of_day,
                'most_productive_day': most_productive_day,
                'efficiency_trend': self._calculate_efficiency_trend(sessions),
                'recommendations': self._generate_recommendations(stats, sessions)
            }
            
        except Exception as e:
            raise e
    
    def _get_best_time_of_day(self, sessions: List[PomodoroSession]) -> str:
        """Get best time of day for productivity"""
        if not sessions:
            return "No data"
        
        hour_productivity = {}
        for session in sessions:
            if session.start_time and session.productivity_score:
                hour = session.start_time.hour
                if hour not in hour_productivity:
                    hour_productivity[hour] = []
                hour_productivity[hour].append(session.productivity_score)
        
        if not hour_productivity:
            return "No data"
        
        # Calculate average productivity per hour
        avg_by_hour = {hour: sum(scores) / len(scores) for hour, scores in hour_productivity.items()}
        best_hour = max(avg_by_hour.keys(), key=lambda h: avg_by_hour[h])
        
        return f"{best_hour}:00 - {best_hour + 1}:00"
    
    def _get_most_productive_day(self, sessions: List[PomodoroSession]) -> str:
        """Get most productive day of week"""
        if not sessions:
            return "No data"
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_productivity = {}
        
        for session in sessions:
            if session.start_time and session.productivity_score:
                weekday = session.start_time.weekday()
                if weekday not in day_productivity:
                    day_productivity[weekday] = []
                day_productivity[weekday].append(session.productivity_score)
        
        if not day_productivity:
            return "No data"
        
        # Calculate average productivity per day
        avg_by_day = {day: sum(scores) / len(scores) for day, scores in day_productivity.items()}
        best_day = max(avg_by_day.keys(), key=lambda d: avg_by_day[d])
        
        return day_names[best_day]
    
    def _calculate_efficiency_trend(self, sessions: List[PomodoroSession]) -> List[float]:
        """Calculate efficiency trend over time"""
        if not sessions:
            return []
        
        # Group sessions by date and calculate average efficiency
        daily_efficiency = {}
        for session in sessions:
            if session.start_time and session.efficiency_score > 0:
                date = session.start_time.date()
                if date not in daily_efficiency:
                    daily_efficiency[date] = []
                daily_efficiency[date].append(session.efficiency_score)
        
        # Calculate average efficiency per day
        avg_efficiency = []
        for date in sorted(daily_efficiency.keys()):
            avg = sum(daily_efficiency[date]) / len(daily_efficiency[date])
            avg_efficiency.append(round(avg, 2))
        
        return avg_efficiency[-7:]  # Last 7 days
    
    def _generate_recommendations(self, stats: Dict[str, Any], sessions: List[PomodoroSession]) -> List[str]:
        """Generate productivity recommendations"""
        recommendations = []
        
        completion_rate = (stats['completed_sessions'] / stats['total_sessions'] * 100) if stats['total_sessions'] > 0 else 0
        
        if completion_rate < 70:
            recommendations.append("Try to complete more sessions to improve productivity")
        
        if stats['avg_productivity'] < 6:
            recommendations.append("Consider taking breaks between sessions to maintain focus")
        
        if stats['total_focus_time'] < 120:  # Less than 2 hours
            recommendations.append("Try to increase your daily focus time for better learning outcomes")
        
        focus_sessions = [s for s in sessions if s.session_type == SessionType.FOCUS]
        if len(focus_sessions) > 0:
            avg_duration = sum([s.duration for s in focus_sessions]) / len(focus_sessions)
            if avg_duration < 20:
                recommendations.append("Consider using longer focus sessions (25+ minutes) for better deep work")
        
        return recommendations
