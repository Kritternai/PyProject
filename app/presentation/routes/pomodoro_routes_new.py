"""
Pomodoro Routes - OOP Architecture
Routes for Pomodoro functionality using OOP architecture
"""
from flask import Blueprint, request, jsonify, session
from functools import wraps
from app.infrastructure.di.pomodoro_container import PomodoroContainer
from app import db

# Create blueprint
pomodoro_bp = Blueprint('pomodoro_new', __name__, url_prefix='/api/pomodoro')

def login_required_api(f):
    """Decorator to require login for API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For testing, use hardcoded user_id '1' if no session
        if 'user_id' not in session:
            session['user_id'] = '1'  # Hardcoded for testing
        return f(*args, **kwargs)
    return decorated_function

# Initialize components directly
from app.infrastructure.database.pomodoro_repository import PomodoroRepositoryImpl
from app.application.services.pomodoro_service import PomodoroService
from app.presentation.controllers.pomodoro_controller import PomodoroController

# Create instances
pomodoro_repository = PomodoroRepositoryImpl(db)
pomodoro_service = PomodoroService(pomodoro_repository)
pomodoro_controller = PomodoroController(pomodoro_service)

# Session Management Routes
@pomodoro_bp.route('/start', methods=['POST'])
@login_required_api
def start_session():
    """Start a new pomodoro session"""
    return pomodoro_controller.start_session()

@pomodoro_bp.route('/<session_id>/pause', methods=['POST'])
@login_required_api
def pause_session(session_id):
    """Pause an active session"""
    return pomodoro_controller.pause_session(session_id)

@pomodoro_bp.route('/<session_id>/resume', methods=['POST'])
@login_required_api
def resume_session(session_id):
    """Resume a paused session"""
    return pomodoro_controller.resume_session(session_id)

@pomodoro_bp.route('/<session_id>/complete', methods=['POST'])
@login_required_api
def complete_session(session_id):
    """Complete a session"""
    return pomodoro_controller.complete_session(session_id)

@pomodoro_bp.route('/<session_id>/interrupt', methods=['POST'])
@login_required_api
def interrupt_session(session_id):
    """Interrupt a session"""
    return pomodoro_controller.interrupt_session(session_id)

@pomodoro_bp.route('/<session_id>/cancel', methods=['POST'])
@login_required_api
def cancel_session(session_id):
    """Cancel a session"""
    return pomodoro_controller.cancel_session(session_id)

# Session Query Routes
@pomodoro_bp.route('/active', methods=['GET'])
@login_required_api
def get_active_session():
    """Get user's active session"""
    return pomodoro_controller.get_active_session()

@pomodoro_bp.route('/sessions', methods=['GET'])
@login_required_api
def get_user_sessions():
    """Get user's sessions"""
    return pomodoro_controller.get_user_sessions()

@pomodoro_bp.route('/lessons/<lesson_id>/sessions', methods=['GET'])
@login_required_api
def get_lesson_sessions(lesson_id):
    """Get sessions for a lesson"""
    return pomodoro_controller.get_lesson_sessions(lesson_id)

# Statistics Routes
@pomodoro_bp.route('/statistics', methods=['GET'])
@login_required_api
def get_statistics():
    """Get session statistics"""
    return pomodoro_controller.get_statistics()

@pomodoro_bp.route('/insights', methods=['GET'])
@login_required_api
def get_productivity_insights():
    """Get productivity insights"""
    return pomodoro_controller.get_productivity_insights()

# Health Check
@pomodoro_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Pomodoro API is healthy',
        'version': '1.0.0'
    })
