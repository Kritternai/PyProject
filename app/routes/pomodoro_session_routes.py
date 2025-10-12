"""
Pomodoro Session Routes
Routes for managing Pomodoro sessions
"""

from flask import Blueprint
from app.controllers.pomodoro_session_controller import PomodoroSessionController

# Create blueprint
pomodoro_session_bp = Blueprint('pomodoro_session', __name__, url_prefix='/api/pomodoro/session')

DB_PATH = 'instance/site.db'


# Create controller instance
session_controller = PomodoroSessionController()

# Session routes
@pomodoro_session_bp.route('', methods=['POST'])
def create_session():
    """Create new session"""
    return session_controller.create_session()


@pomodoro_session_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    return session_controller.get_session(session_id)

@pomodoro_session_bp.route('/user', methods=['GET'])
def get_user_sessions():
    """Get all sessions for current user"""
    return session_controller.get_user_sessions()

@pomodoro_session_bp.route('/<session_id>', methods=['PUT'])
def update_session(session_id):
    """Update session"""
    return session_controller.update_session(session_id)

@pomodoro_session_bp.route('/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """End session"""
    return session_controller.end_session(session_id)

@pomodoro_session_bp.route('/active', methods=['GET'])
def get_active_session():
    """Get active session"""
    return session_controller.get_active_session()

@pomodoro_session_bp.route('/<session_id>/interrupt', methods=['POST'])
def interrupt_session(session_id):
    """Interrupt session"""
    return session_controller.interrupt_session(session_id)



