"""
Main routes for OOP architecture.
Clean routes that integrate with the new OOP system.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify
from functools import wraps
from .presentation.middleware.auth_middleware import login_required, get_current_user
from .infrastructure.di.container import get_service
from .domain.interfaces.services.user_service import UserService
from .domain.interfaces.services.lesson_service import LessonService
from .domain.interfaces.services.note_service import NoteService
from .domain.interfaces.services.task_service import TaskService

# Create main blueprint
main_bp = Blueprint('main', __name__)

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('register.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.before_request
def load_logged_in_user():
    """Load logged in user for web routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = get_service(UserService)
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Main index page."""
    # Check if user is logged in
    if 'user_id' in session:
        return redirect(url_for('register.dashboard'))
    
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected)

@main_bp.route('/dashboard')
@login_required_web
def dashboard():
    """Dashboard page."""
    if not g.user:
        return redirect(url_for('register.login'))
    return render_template('base.html', user=g.user)

@main_bp.route('/partial/dashboard')
@login_required_web
def partial_dashboard():
    """Dashboard partial for SPA."""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dashboard_fragment.html', user=g.user)

@main_bp.route('/partial/class')
@login_required_web
def partial_class():
    """Class/Lessons partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        lesson_service = get_service(LessonService)
        lessons = lesson_service.get_user_lessons(g.user.id)
        return render_template('class_fragment.html', lessons=lessons, user=g.user)
    except Exception as e:
        return render_template('class_fragment.html', lessons=[], user=g.user)

@main_bp.route('/partial/note')
@login_required_web
def partial_note():
    """Note partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        note_service = get_service(NoteService)
        notes = note_service.get_user_notes(g.user.id)
        return render_template('note_fragment.html', notes=notes, user=g.user)
    except Exception as e:
        return render_template('note_fragment.html', notes=[], user=g.user)

@main_bp.route('/partial/track')
@login_required_web
def partial_track():
    """Track/Progress Tracking partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        # For now, just return the tracking fragment
        # Later we can add task service integration
        return render_template('track_fragment.html', user=g.user)
    except Exception as e:
        return render_template('track_fragment.html', user=g.user)

@main_bp.route('/partial/pomodoro')
@login_required_web
def partial_pomodoro():
    """Pomodoro timer partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        # Return the pomodoro fragment
        return render_template('pomodoro_fragment.html', user=g.user)
    except Exception as e:
        return render_template('pomodoro_fragment.html', user=g.user)

@main_bp.route('/partial/dev')
@login_required_web
def partial_dev():
    """Development partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dev_fragment.html', user=g.user)

# API endpoints for AJAX calls
@main_bp.route('/api/lessons/data')
@login_required_web
def lessons_data():
    """Get lessons data for AJAX"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = get_service(LessonService)
        lessons = lesson_service.get_user_lessons(g.user.id)
        return jsonify({
            'success': True,
            'data': [lesson.to_dict() for lesson in lessons]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/notes/data')
@login_required_web
def notes_data():
    """Get notes data for AJAX"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = get_service(NoteService)
        notes = note_service.get_user_notes(g.user.id)
        return jsonify({
            'success': True,
            'data': [note.to_dict() for note in notes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/tasks/data')
@login_required_web
def tasks_data():
    """Get tasks data for AJAX"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        task_service = get_service(TaskService)
        tasks = task_service.get_user_tasks(g.user.id)
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Legacy routes for backward compatibility - removed to prevent redirect loops
# All authentication routes are now handled by register_bp
