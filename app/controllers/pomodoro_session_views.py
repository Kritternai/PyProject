"""
Pomodoro Session Views module for handling session-related operations.
Follows Clean Architecture principles for separation of concerns.
"""

from flask import jsonify, request, g
from typing import Dict, Any
from app.services.pomodoro_session_service import PomodoroSessionService
from app.utils.exceptions import ValidationException

class PomodoroSessionViews:
    """Views for Pomodoro session operations"""

    def __init__(self):
        self._session_service = PomodoroSessionService()

    def create_session(self) -> Dict[str, Any]:
        """Create a new Pomodoro session"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request data is required'}), 400

            required_fields = ['session_type', 'duration']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400

            session = self._session_service.create_session(
                user_id=g.user.id,
                session_type=data['session_type'],
                duration=data['duration'],
                task=data.get('task')
            )

            return jsonify({
                'success': True,
                'session': session.to_dict()
            }), 201

        except ValidationException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            session = self._session_service.get_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404

            if session.user_id != g.user.id:
                return jsonify({'error': 'Unauthorized access'}), 403

            return jsonify({
                'success': True,
                'session': session.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_user_sessions(self) -> Dict[str, Any]:
        """Get all sessions for current user"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            sessions = self._session_service.get_user_sessions(g.user.id)
            return jsonify({
                'success': True,
                'sessions': [session.to_dict() for session in sessions]
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def update_session(self, session_id: str) -> Dict[str, Any]:
        """Update session details"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            session = self._session_service.get_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404

            if session.user_id != g.user.id:
                return jsonify({'error': 'Unauthorized access'}), 403

            data = request.get_json()
            if not data:
                return jsonify({'error': 'No update data provided'}), 400

            updated_session = self._session_service.update_session(session_id, data)
            return jsonify({
                'success': True,
                'session': updated_session.to_dict()
            }), 200

        except ValidationException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a Pomodoro session"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            session = self._session_service.get_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404

            if session.user_id != g.user.id:
                return jsonify({'error': 'Unauthorized access'}), 403

            ended_session = self._session_service.end_session(session_id)
            return jsonify({
                'success': True,
                'session': ended_session.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def get_active_session(self) -> Dict[str, Any]:
        """Get user's active session"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            session = self._session_service.get_active_session(g.user.id)
            if not session:
                return jsonify({'message': 'No active session found'}), 404

            return jsonify({
                'success': True,
                'session': session.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    def interrupt_session(self, session_id: str) -> Dict[str, Any]:
        """Interrupt a Pomodoro session"""
        try:
            if not g.user:
                return jsonify({'error': 'Authentication required'}), 401

            session = self._session_service.get_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found'}), 404

            if session.user_id != g.user.id:
                return jsonify({'error': 'Unauthorized access'}), 403

            interrupted_session = self._session_service.interrupt_session(session_id)
            return jsonify({
                'success': True,
                'session': interrupted_session.to_dict()
            }), 200

        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500