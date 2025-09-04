"""
Web routes for displaying HTML pages using OOP architecture.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, flash
from functools import wraps
from ..middleware.auth_middleware import login_required, get_current_user
from ...infrastructure.di.container import get_service
from ...domain.interfaces.services.user_service import UserService
from ...domain.interfaces.services.lesson_service import LessonService
from ...domain.interfaces.services.note_service import NoteService
from ...domain.interfaces.services.task_service import TaskService
from ...shared.exceptions import NotFoundException, ValidationException, BusinessLogicException

# Create web blueprint
web_bp = Blueprint('web', __name__)

def login_required_web(f):
    """Login required decorator for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

@web_bp.before_request
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

@web_bp.route('/')
@web_bp.route('/index')
def index():
    """Home page"""
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected)

# Login and register routes moved to auth_web_routes.py

# Dashboard route moved to auth_web_routes.py

# Lessons, notes, tasks routes moved to auth_web_routes.py

# Profile route moved to auth_web_routes.py

# Logout route moved to auth_web_routes.py

# Partial routes for AJAX loading
# Partial dashboard route moved to auth_web_routes.py

# Partial register and login routes moved to auth_web_routes.py

# Partial class, note, track routes moved to auth_web_routes.py

# API endpoints moved to auth_web_routes.py
