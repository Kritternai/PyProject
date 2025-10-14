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
            return render_template('pomodoro_fragment.html')
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

    # Task Management Methods
    def create_task(self) -> Dict[str, Any]:
        """Create a new task for Pomodoro tracking."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            if not data or 'title' not in data:
                return jsonify({'error': 'Task title is required'}), 400

            task = self._pomodoro_service.create_task(
                user_id=g.user.id,
                title=data['title'],
                description=data.get('description'),
                estimated_pomodoros=data.get('estimated_pomodoros', 1)
            )

            return jsonify({
                'success': True,
                'task': task.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_user_tasks(self) -> Dict[str, Any]:
        """Get all tasks for current user."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            tasks = self._pomodoro_service.get_tasks_by_user(g.user.id)
            return jsonify({
                'success': True,
                'tasks': [task.to_dict() for task in tasks]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def update_task(self) -> Dict[str, Any]:
        """Update task details."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            if not data or 'task_id' not in data:
                return jsonify({'error': 'Task ID is required'}), 400

            task = self._pomodoro_service.update_task(
                user_id=g.user.id,
                task_id=data['task_id'],
                title=data.get('title'),
                description=data.get('description'),
                status=data.get('status'),
                completed=data.get('completed')
            )

            return jsonify({
                'success': True,
                'task': task.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

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

    # Analytics and Reports Methods
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

    # Notification Management Methods
    def update_notification_settings(self) -> Dict[str, Any]:
        """Update notification preferences."""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            settings = self._pomodoro_service.update_notification_settings(
                user_id=g.user.id,
                sound_enabled=data.get('sound_enabled'),
                desktop_notifications=data.get('desktop_notifications'),
                break_reminders=data.get('break_reminders')
            )

            return jsonify({
                'success': True,
                'settings': settings
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Data Export Methods
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
