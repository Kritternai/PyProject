"""
Simple Pomodoro Statistics Service
Independent from main services.py to avoid circular imports
"""

from datetime import datetime, date
from typing import Dict, Any

class SimplePomodoroStatisticsService:
    """Simple statistics service without complex dependencies"""

    def get_daily_statistics(self, user_id: str, target_date=None) -> Dict[str, Any]:
        """Get basic daily statistics"""
        if target_date is None:
            target_date = date.today()
        
        # Return basic mock data for now to avoid circular imports
        return {
            'total_sessions': 3,
            'total_focus_sessions': 2,
            'total_focus_time': 50,
            'total_break_time': 10,
            'total_completed_sessions': 2,
            'total_interrupted_sessions': 1,
            'productivity_score': 7.5,
            'total_tasks_completed': 1,
            'total_tasks': 2,
            'date': target_date.isoformat() if hasattr(target_date, 'isoformat') else str(target_date)
        }

    def get_weekly_statistics(self, user_id: str, start_date=None) -> list:
        """Get basic weekly statistics"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        stats = []
        
        for i, day in enumerate(days):
            stats.append({
                'date': f'2024-10-{14+i:02d}',
                'total_sessions': 2 + i % 3,
                'total_focus_time': 25 * (2 + i % 3),
                'productivity_score': 6 + (i % 4),
                'total_completed_sessions': 1 + i % 2
            })
        
        return stats

    def get_monthly_statistics(self, user_id: str, year=None, month=None) -> list:
        """Get basic monthly statistics"""
        return self.get_weekly_statistics(user_id)  # Simple placeholder

    def get_productivity_trends(self, user_id: str, days=7) -> Dict[str, Any]:
        """Get basic productivity trends"""
        return {
            'trend': 'improving',
            'average_productivity': 7.2,
            'total_focus_time': 200,
            'completion_rate': 85.0,
            'data_points': self.get_weekly_statistics(user_id)
        }

    def get_statistics_summary(self, user_id: str) -> Dict[str, Any]:
        """Get basic statistics summary"""
        today_stats = self.get_daily_statistics(user_id)
        
        return {
            'today': today_stats,
            'this_week': {
                'total_focus_time': 200,
                'total_sessions': 12,
                'average_productivity': 7.2
            },
            'trends': {
                'trend': 'improving',
                'average_productivity': 7.2
            },
            'last_updated': datetime.utcnow().isoformat()
        }

    def get_chart_data(self, chart_type='weekly') -> Dict[str, Any]:
        """Get basic chart data"""
        if chart_type == 'weekly':
            return {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'focus_time': [25, 50, 25, 75, 50, 25, 50],
                'productivity': [7, 8, 6, 9, 7, 6, 8],
                'completion_rate': [80, 90, 70, 95, 85, 75, 88]
            }
        else:
            return {
                'daily': self.get_daily_statistics('dummy'),
                'pie_chart': {
                    'focus_time': 50,
                    'break_time': 10,
                    'long_break_time': 5
                }
            }