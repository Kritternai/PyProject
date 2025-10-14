"""
Pomodoro Statistics Controller
Handles HTTP requests for statistics operations following MVC pattern
"""

from flask import request, jsonify, session as flask_session
from datetime import datetime, date
from typing import Dict, Any
import traceback

from app.simple_pomodoro_stats import SimplePomodoroStatisticsService

class PomodoroStatisticsController:
    """Controller for Pomodoro statistics operations"""

    def __init__(self):
        self.stats_service = SimplePomodoroStatisticsService()

    def _get_current_user_id(self) -> str:
        """Get current user ID from session"""
        user_id = flask_session.get('user_id')
        if not user_id:
            raise ValueError("User not logged in")
        return user_id

    def get_daily_statistics(self) -> Dict[str, Any]:
        """Get daily statistics"""
        try:
            user_id = self._get_current_user_id()
            
            # Get date parameter
            date_param = request.args.get('date')
            target_date = None
            
            if date_param:
                try:
                    target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD")
            
            statistics = self.stats_service.get_daily_statistics(user_id, target_date)
            
            return {
                'success': True,
                'data': statistics,
                'message': f'Daily statistics retrieved for {target_date or date.today()}'
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Invalid request parameters'
            }, 400
            
        except Exception as e:
            print(f"Error getting daily statistics: {str(e)}")
            return {
                'success': False,
                'error': 'Internal server error',
                'message': 'Failed to retrieve daily statistics'
            }, 500

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get overall statistics summary"""
        try:
            user_id = self._get_current_user_id()
            
            summary = self.stats_service.get_statistics_summary(user_id)
            
            return {
                'success': True,
                'data': summary,
                'message': 'Statistics summary retrieved successfully'
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Invalid request parameters'
            }, 400
            
        except Exception as e:
            print(f"Error getting statistics summary: {str(e)}")
            return {
                'success': False,
                'error': 'Internal server error',
                'message': 'Failed to retrieve statistics summary'
            }, 500

    def get_chart_data(self) -> Dict[str, Any]:
        """Get data formatted for charts"""
        try:
            user_id = self._get_current_user_id()
            
            chart_type = request.args.get('type', 'weekly')
            chart_data = self.stats_service.get_chart_data(chart_type)
            
            return {
                'success': True,
                'data': chart_data,
                'message': 'Chart data retrieved successfully'
            }
            
        except Exception as e:
            print(f"Error getting chart data: {str(e)}")
            return {
                'success': False,
                'error': 'Internal server error',
                'message': 'Failed to retrieve chart data'
            }, 500

    # Placeholder methods for other endpoints  
    def get_weekly_statistics(self) -> Dict[str, Any]:
        try:
            user_id = self._get_current_user_id()
            data = self.stats_service.get_weekly_statistics(user_id)
            return {'success': True, 'data': data, 'message': 'Weekly statistics retrieved'}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

    def get_monthly_statistics(self) -> Dict[str, Any]:
        try:
            user_id = self._get_current_user_id()
            data = self.stats_service.get_monthly_statistics(user_id)
            return {'success': True, 'data': data, 'message': 'Monthly statistics retrieved'}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

    def get_productivity_trends(self) -> Dict[str, Any]:
        try:
            user_id = self._get_current_user_id()
            days = request.args.get('days', default=7, type=int)
            data = self.stats_service.get_productivity_trends(user_id, days)
            return {'success': True, 'data': data, 'message': 'Trends retrieved'}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500

    def update_daily_statistics(self) -> Dict[str, Any]:
        return {'success': True, 'message': 'Statistics updated (placeholder)'}

    def delete_daily_statistics(self) -> Dict[str, Any]:
        return {'success': False, 'error': 'Not implemented', 'message': 'Delete not available'}, 404

    def recalculate_all_statistics(self) -> Dict[str, Any]:
        return {'success': True, 'message': 'Statistics recalculated (placeholder)'}

    def get_statistics_chart_data(self) -> Dict[str, Any]:
        return self.get_chart_data()
