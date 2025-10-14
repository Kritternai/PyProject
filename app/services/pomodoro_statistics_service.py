"""
Pomodoro Statistics Service Layer
Handles business logic for statistics calculations and management
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from app import db
from app.models.pomodoro_statistics import PomodoroStatisticsModel
from app.models.pomodoro_session import PomodoroSessionModel
import uuid

class PomodoroStatisticsService:
    """Service layer for Pomodoro statistics management"""

    def get_daily_statistics(self, user_id: str, target_date: date = None) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific date"""
        if target_date is None:
            target_date = date.today()
            
        stats = PomodoroStatisticsModel.query.filter_by(
            user_id=user_id,
            date=target_date
        ).first()
        
        if stats:
            return stats.to_dict()
        
        # If no statistics exist, create from session data
        return self.calculate_daily_statistics(user_id, target_date)

    def get_weekly_statistics(self, user_id: str, start_date: date = None) -> List[Dict[str, Any]]:
        """Get statistics for a week (7 days)"""
        if start_date is None:
            # Get start of current week (Monday)
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        stats = PomodoroStatisticsModel.query.filter(
            PomodoroStatisticsModel.user_id == user_id,
            PomodoroStatisticsModel.date >= start_date,
            PomodoroStatisticsModel.date <= end_date
        ).order_by(PomodoroStatisticsModel.date).all()
        
        return [stat.to_dict() for stat in stats]

    def get_monthly_statistics(self, user_id: str, year: int = None, month: int = None) -> List[Dict[str, Any]]:
        """Get statistics for a month"""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month
            
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        stats = PomodoroStatisticsModel.query.filter(
            PomodoroStatisticsModel.user_id == user_id,
            PomodoroStatisticsModel.date >= start_date,
            PomodoroStatisticsModel.date <= end_date
        ).order_by(PomodoroStatisticsModel.date).all()
        
        return [stat.to_dict() for stat in stats]

    def calculate_daily_statistics(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """Calculate statistics from session data for a specific date"""
        # Get all sessions for the target date
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        sessions = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.created_at >= start_datetime,
            PomodoroSessionModel.created_at <= end_datetime
        ).all()
        
        # Initialize statistics
        stats = {
            'total_sessions': 0,
            'total_focus_sessions': 0,
            'total_short_break_sessions': 0,
            'total_long_break_sessions': 0,
            'total_focus_time': 0,
            'total_break_time': 0,
            'total_long_break_time': 0,
            'total_time_spent': 0,
            'total_completed_sessions': 0,
            'total_interrupted_sessions': 0,
            'total_abandoned_sessions': 0,
            'total_productivity_score': 0,
            'total_tasks_completed': 0,
            'total_tasks': 0,
            'total_effective_time': 0,
            'total_ineffective_time': 0,
            'total_on_time_sessions': 0,
            'total_late_sessions': 0,
            'average_session_duration': 0.0,
            'productivity_score': 0.0
        }
        
        # Calculate statistics from sessions
        productivity_scores = []
        session_durations = []
        
        for session in sessions:
            stats['total_sessions'] += 1
            
            # Count by session type
            if session.session_type == 'focus':
                stats['total_focus_sessions'] += 1
                if session.actual_duration:
                    stats['total_focus_time'] += session.actual_duration
            elif session.session_type == 'short_break':
                stats['total_short_break_sessions'] += 1
                if session.actual_duration:
                    stats['total_break_time'] += session.actual_duration
            elif session.session_type == 'long_break':
                stats['total_long_break_sessions'] += 1
                if session.actual_duration:
                    stats['total_long_break_time'] += session.actual_duration
            
            # Count by status
            if session.is_completed:
                stats['total_completed_sessions'] += 1
            if session.is_interrupted:
                stats['total_interrupted_sessions'] += 1
            if session.status == 'abandoned':
                stats['total_abandoned_sessions'] += 1
            
            # Time calculations
            if session.actual_duration:
                stats['total_time_spent'] += session.actual_duration
                session_durations.append(session.actual_duration)
                
                # Effective vs ineffective time
                if session.is_completed and session.productivity_score and session.productivity_score >= 7:
                    stats['total_effective_time'] += session.actual_duration
                else:
                    stats['total_ineffective_time'] += session.actual_duration
            
            # Productivity scoring
            if session.productivity_score:
                stats['total_productivity_score'] += session.productivity_score
                productivity_scores.append(session.productivity_score)
            
            # Task tracking
            if session.task:
                stats['total_tasks'] += 1
                if session.is_completed:
                    stats['total_tasks_completed'] += 1
            
            # On-time vs late sessions
            if session.actual_duration and session.duration:
                if session.actual_duration >= session.duration * 0.9:  # 90% or more is on-time
                    stats['total_on_time_sessions'] += 1
                else:
                    stats['total_late_sessions'] += 1
        
        # Calculate averages
        if session_durations:
            stats['average_session_duration'] = sum(session_durations) / len(session_durations)
        
        if productivity_scores:
            stats['productivity_score'] = sum(productivity_scores) / len(productivity_scores)
        
        return stats

    def update_or_create_daily_statistics(self, user_id: str, target_date: date = None) -> Dict[str, Any]:
        """Update or create daily statistics"""
        if target_date is None:
            target_date = date.today()
        
        # Check if statistics already exist
        existing_stats = PomodoroStatisticsModel.query.filter_by(
            user_id=user_id,
            date=target_date
        ).first()
        
        # Calculate fresh statistics
        calculated_stats = self.calculate_daily_statistics(user_id, target_date)
        
        if existing_stats:
            # Update existing record
            for key, value in calculated_stats.items():
                if hasattr(existing_stats, key):
                    setattr(existing_stats, key, value)
            existing_stats.updated_at = datetime.utcnow()
            db.session.commit()
            return existing_stats.to_dict()
        else:
            # Create new record
            new_stats = PomodoroStatisticsModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                date=target_date,
                **calculated_stats
            )
            db.session.add(new_stats)
            db.session.commit()
            return new_stats.to_dict()

    def get_productivity_trends(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get productivity trends over specified days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        stats = PomodoroStatisticsModel.query.filter(
            PomodoroStatisticsModel.user_id == user_id,
            PomodoroStatisticsModel.date >= start_date,
            PomodoroStatisticsModel.date <= end_date
        ).order_by(PomodoroStatisticsModel.date).all()
        
        if not stats:
            return {
                'trend': 'neutral',
                'average_productivity': 0.0,
                'total_focus_time': 0,
                'completion_rate': 0.0,
                'data_points': []
            }
        
        # Calculate trends
        productivity_scores = [s.productivity_score for s in stats if s.productivity_score > 0]
        focus_times = [s.total_focus_time for s in stats]
        completion_rates = []
        
        for s in stats:
            if s.total_sessions > 0:
                completion_rates.append(s.total_completed_sessions / s.total_sessions * 100)
            else:
                completion_rates.append(0)
        
        # Determine trend
        if len(productivity_scores) >= 2:
            recent_avg = sum(productivity_scores[-3:]) / len(productivity_scores[-3:])
            earlier_avg = sum(productivity_scores[:-3]) / len(productivity_scores[:-3]) if len(productivity_scores) > 3 else productivity_scores[0]
            
            if recent_avg > earlier_avg + 0.5:
                trend = 'improving'
            elif recent_avg < earlier_avg - 0.5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'neutral'
        
        return {
            'trend': trend,
            'average_productivity': sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0.0,
            'total_focus_time': sum(focus_times),
            'completion_rate': sum(completion_rates) / len(completion_rates) if completion_rates else 0.0,
            'data_points': [s.to_dict() for s in stats]
        }

    def get_statistics_summary(self, user_id: str) -> Dict[str, Any]:
        """Get overall statistics summary"""
        today_stats = self.get_daily_statistics(user_id)
        week_stats = self.get_weekly_statistics(user_id)
        trends = self.get_productivity_trends(user_id, 7)
        
        # Calculate weekly totals
        week_totals = {
            'total_focus_time': sum(s.get('total_focus_time', 0) for s in week_stats),
            'total_sessions': sum(s.get('total_sessions', 0) for s in week_stats),
            'average_productivity': 0.0
        }
        
        week_productivity_scores = [s.get('productivity_score', 0) for s in week_stats if s.get('productivity_score', 0) > 0]
        if week_productivity_scores:
            week_totals['average_productivity'] = sum(week_productivity_scores) / len(week_productivity_scores)
        
        return {
            'today': today_stats,
            'this_week': week_totals,
            'trends': trends,
            'last_updated': datetime.utcnow().isoformat()
        }

    def delete_statistics(self, user_id: str, target_date: date) -> bool:
        """Delete statistics for a specific date"""
        stats = PomodoroStatisticsModel.query.filter_by(
            user_id=user_id,
            date=target_date
        ).first()
        
        if stats:
            db.session.delete(stats)
            db.session.commit()
            return True
        return False

    def recalculate_all_statistics(self, user_id: str) -> Dict[str, Any]:
        """Recalculate all statistics for a user"""
        # Get all dates with sessions
        sessions = PomodoroSessionModel.query.filter_by(user_id=user_id).all()
        
        if not sessions:
            return {'message': 'No sessions found', 'updated_dates': []}
        
        # Get unique dates
        session_dates = set()
        for session in sessions:
            session_dates.add(session.created_at.date())
        
        updated_dates = []
        for session_date in session_dates:
            self.update_or_create_daily_statistics(user_id, session_date)
            updated_dates.append(session_date.isoformat())
        
        return {
            'message': f'Recalculated statistics for {len(updated_dates)} dates',
            'updated_dates': updated_dates
        }
