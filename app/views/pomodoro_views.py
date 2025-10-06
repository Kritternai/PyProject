"""
Pomodoro Timer views module for handling timer-related operations.
Follows Clean Architecture principles for separation of concerns.
"""

from flask import request, jsonify, g, render_template
from typing import Dict, Any
from app.services import PomodoroService
from app.utils.exceptions import ValidationException, AuthenticationException
from ..middleware import login_required


class PomodoroController:
    """Handles all Pomodoro timer related HTTP requests and responses."""

    def __init__(self):
        self._pomodoro_service = PomodoroService()

    def render_pomodoro_page(self) -> str:
        """Render the main Pomodoro timer page."""
        try:
            if not g.user:
                return render_template('login.html')
            return render_template('pomodoro.html')
        except Exception as e:
            return render_template('error.html', error=str(e))

    def start_timer(self) -> Dict[str, Any]:
        """Start a new Pomodoro session."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            if not data or 'duration' not in data:
                return jsonify({'error': 'Duration is required'}), 400

            timer = self._pomodoro_service.start_timer(
                user_id=g.user.id,
                duration=data['duration'],
                task_id=data.get('task_id'),
                description=data.get('description')
            )

            return jsonify({
                'success': True,
                'timer': timer.to_dict()
            }), 200

        except ValidationException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def stop_timer(self) -> Dict[str, Any]:
        """Stop the current Pomodoro session."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            self._pomodoro_service.stop_timer(g.user.id)
            return jsonify({'success': True}), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_timer_state(self) -> Dict[str, Any]:
        """Get current timer state and remaining time."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            timer_state = self._pomodoro_service.get_timer_state(g.user.id)
            return jsonify({
                'success': True,
                'state': timer_state
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

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

    def update_timer_settings(self) -> Dict[str, Any]:
        """Update user's timer preferences."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            if not data:
                return jsonify({'error': 'Settings data is required'}), 400

            settings = self._pomodoro_service.update_settings(
                user_id=g.user.id,
                work_duration=data.get('work_duration'),
                break_duration=data.get('break_duration'),
                long_break_duration=data.get('long_break_duration'),
                long_break_interval=data.get('long_break_interval'),
                auto_start_breaks=data.get('auto_start_breaks'),
                auto_start_pomodoros=data.get('auto_start_pomodoros'),
                daily_target=data.get('daily_target')
            )

            return jsonify({
                'success': True,
                'settings': settings
            }), 200

        except ValidationException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_timer_settings(self) -> Dict[str, Any]:
        """Get user's timer preferences."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            settings = self._pomodoro_service.get_settings(g.user.id)
            return jsonify({
                'success': True,
                'settings': settings
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def toggle_timer(self) -> Dict[str, Any]:
        """Pause or resume the current timer."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            timer_state = self._pomodoro_service.toggle_timer(g.user.id)
            return jsonify({
                'success': True,
                'state': timer_state
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def skip_break(self) -> Dict[str, Any]:
        """Skip the current break period."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            timer_state = self._pomodoro_service.skip_break(g.user.id)
            return jsonify({
                'success': True,
                'state': timer_state
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
