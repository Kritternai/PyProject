"""
Pomodoro Session Routes
Routes for managing Pomodoro sessions
"""

from flask import Blueprint
from app.controllers.pomodoro_session_views import PomodoroSessionViews
from app.middleware.auth_middleware import login_required

# Create blueprint
pomodoro_session_bp = Blueprint('pomodoro_session', __name__, url_prefix='/api/pomodoro/session')

# Create controller instance
session_views = PomodoroSessionViews()

# Session routes
@pomodoro_session_bp.route('', methods=['POST'])
def create_session():
    """Create new session"""
    return session_views.create_session()

@pomodoro_session_bp.route('/<session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """Get session details"""
    return session_views.get_session(session_id)

@pomodoro_session_bp.route('/user', methods=['GET'])
@login_required
def get_user_sessions():
    """Get all sessions for current user"""
    return session_views.get_user_sessions()

@pomodoro_session_bp.route('/<session_id>', methods=['PUT'])
@login_required
def update_session(session_id):
    """Update session"""
    return session_views.update_session(session_id)

@pomodoro_session_bp.route('/<session_id>/end', methods=['POST'])
@login_required
def end_session(session_id):
    """End session"""
    return session_views.end_session(session_id)

@pomodoro_session_bp.route('/active', methods=['GET'])
@login_required
def get_active_session():
    """Get active session"""
    return session_views.get_active_session()

@pomodoro_session_bp.route('/<session_id>/interrupt', methods=['POST'])
@login_required
def interrupt_session(session_id):
    """Interrupt session"""
    return session_views.interrupt_session(session_id)



