"""
Pomodoro Statistics Views module for handling statistics-related operations.
Follows Clean Architecture principles for separation of concerns.
"""

from flask import request, jsonify, g
from typing import Dict, Any
from app.services import PomodoroService
from app.utils.exceptions import ValidationException


class PomodoroStatisticsViews:
    """Views for Pomodoro statistics operations"""

    def __init__(self):
        self._pomodoro_service = PomodoroService()

    def get_timer_stats(self) -> Dict[str, Any]:
        """Get user's timer statistics."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            stats = self._pomodoro_service.get_stats(g.user.id)
            return jsonify({
                'success': True,
                'stats': stats
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_daily_progress(self) -> Dict[str, Any]:
        """Get user's progress towards daily target."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            progress = self._pomodoro_service.get_daily_progress(g.user.id)
            return jsonify({
                'success': True,
                'progress': progress
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_productivity_report(self) -> Dict[str, Any]:
        """Get detailed productivity report."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json() or {}
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            report = self._pomodoro_service.generate_productivity_report(
                user_id=g.user.id,
                start_date=start_date,
                end_date=end_date
            )

            return jsonify({
                'success': True,
                'report': report
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_session_history(self) -> Dict[str, Any]:
        """Get user's Pomodoro session history."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            history = self._pomodoro_service.get_session_history(g.user.id)
            return jsonify({
                'success': True,
                'history': history
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def export_data(self) -> Dict[str, Any]:
        """Export user's Pomodoro data."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = self._pomodoro_service.export_user_data(g.user.id)
            return jsonify({
                'success': True,
                'data': data
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500