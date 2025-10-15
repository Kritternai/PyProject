"""
Pomodoro Session Views module for handling session-related operations.
Follows Clean Architecture principles for separation of concerns.
"""

from flask import jsonify, request, g
from typing import Dict, Any
from app.services import PomodoroSessionService
from app.utils.exceptions import ValidationException

class PomodoroSessionViews:
    """Views for Pomodoro session operations"""

    def __init__(self):
        self._session_service = PomodoroSessionService()

    def create_session(self) -> Dict[str, Any]:
        """Create a new Pomodoro session"""
        try:
            # Check authentication first
            if not hasattr(g, 'user') or not g.user:
                return jsonify({
                    'error': 'Authentication Required',
                    'message': 'User must be logged in to create Pomodoro session',
                    'code': 'AUTH_REQUIRED'
                }), 401

            user_id = g.user.id
            print(f"🍅 Creating session for user: {user_id}")

            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Request data is required',
                    'code': 'MISSING_DATA'
                }), 400

            required_fields = ['session_type', 'duration']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': 'Bad Request', 
                    'message': f'Missing required fields: {", ".join(missing_fields)}',
                    'code': 'MISSING_FIELDS'
                }), 400

            # Create session with all available data
            session = self._session_service.create_session(
                user_id=user_id,
                session_type=data['session_type'],
                duration=data['duration'],
                task=data.get('task'),
                lesson_id=data.get('lesson_id'),
                section_id=data.get('section_id'),
                mood_before=data.get('mood_before'),
                energy_level=data.get('energy_level'),
                auto_start_next=data.get('auto_start_next', True),
                notification_enabled=data.get('notification_enabled', True),
                sound_enabled=data.get('sound_enabled', True)
            )

            print(f"✅ Session created successfully:")
            print(f"   - Session ID: {session.id}")
            print(f"   - User ID: {session.user_id}")
            print(f"   - Type: {session.session_type}")
            print(f"   - Duration: {session.duration}")
            print(f"   - Status: {session.status}")

            return jsonify({
                'success': True,
                'message': 'Session created successfully',
                'session': session.to_dict()
            }), 201

        except ValidationException as e:
            return jsonify({
                'error': 'Validation Error',
                'message': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400
        except Exception as e:
            import traceback
            print(f"Error creating session: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(e),
                'code': 'INTERNAL_ERROR',
                'traceback': traceback.format_exc()
            }), 500

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

            # Get any additional data from request
            data = request.get_json() or {}
            status = data.get('status', 'completed')

            # End the session
            print(f"🏁 Ending session {session_id} for user {g.user.id}")
            ended_session = self._session_service.end_session(session_id, status)
            
            if not ended_session:
                print(f"❌ Failed to end session {session_id}")
                return jsonify({'error': 'Failed to end session'}), 500

            print(f"✅ Session ended successfully:")
            print(f"   - Session ID: {ended_session.id}")
            print(f"   - Status: {ended_session.status}")
            print(f"   - Is completed: {ended_session.is_completed}")
            print(f"   - Actual duration: {ended_session.actual_duration}")

            return jsonify({
                'success': True,
                'message': 'Session ended successfully',
                'session': ended_session.to_dict()
            }), 200

        except ValidationException as e:
            return jsonify({
                'error': 'Validation Error',
                'message': str(e),
                'code': 'VALIDATION_ERROR'
            }), 400
        except Exception as e:
            print(f"❌ Error ending session: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': 'Failed to end session'
            }), 500

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