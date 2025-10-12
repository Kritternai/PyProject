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

    # Break Session Management Methods
    def start_break(self) -> Dict[str, Any]:
        """Start a break session."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            if not data or 'break_type' not in data:
                return jsonify({'error': 'Break type is required'}), 400

            session = self._pomodoro_service.start_break(
                user_id=g.user.id,
                break_type=data['break_type'],
                duration=data.get('duration')
            )

            return jsonify({
                'success': True,
                'session': session.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def end_break(self) -> Dict[str, Any]:
        """End current break session."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            self._pomodoro_service.end_break(g.user.id)
            return jsonify({'success': True}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500