"""
Main Routes
General routes for dashboard, index, and common fragments
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify
from functools import wraps
from ..middleware.auth_middleware import login_required
from ..services import UserService

# Create blueprint
main_routes_bp = Blueprint('main_routes', __name__)


def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@main_routes_bp.before_request
def load_logged_in_user():
    """Load logged in user for web routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None


# ============================================
# INDEX & DASHBOARD
# ============================================

@main_routes_bp.route('/')
@main_routes_bp.route('/index')
def index():
    """Main index page"""
    if 'user_id' in session:
        return redirect(url_for('main_routes.dashboard'))
    
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected, user=None)


@main_routes_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
            user = user_service.get_user_by_id(user_id)
            return render_template('base.html', user=user)
        except Exception:
            return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.login'))


@main_routes_bp.route('/partial/dashboard')
def partial_dashboard():
    """Dashboard fragment for SPA"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dashboard_fragment.html', user=g.user)


# ============================================
# FRAGMENT ROUTES
# ============================================

@main_routes_bp.route('/partial/track')
def partial_track():
    """Track/Progress Tracking fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        return render_template('track_fragment.html', user=g.user)
    except Exception as e:
        return render_template('track_fragment.html', user=g.user)


@main_routes_bp.route('/partial/dev')
def partial_dev():
    """Development fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('dev_fragment.html', user=g.user)


@main_routes_bp.route('/partial/setting')
def partial_setting():
    """Settings fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('setting_fragment.html', user=g.user)


@main_routes_bp.route('/partial/profile')
def partial_profile():
    """Profile fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('profile_fragment.html', user=g.user)


@main_routes_bp.route('/partial/change_password')
def partial_change_password():
    """Change password fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('change_password_fragment.html', user=g.user)


@main_routes_bp.route('/partial/pomodoro')
def partial_pomodoro():
    """Pomodoro timer fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        return render_template('pomodoro_fragment.html', user=g.user)
    except Exception as e:
        return render_template('pomodoro_fragment.html', user=g.user)


@main_routes_bp.route('/partial/pomodoro_statistics')
def partial_pomodoro_statistics():
    """Pomodoro statistics fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        return render_template('pomodoro_statistics_fragment.html', user=g.user)
    except Exception as e:
        return render_template('pomodoro_statistics_fragment.html', user=g.user)


# ============================================
# DIRECT URL ACCESS ROUTES (for SPA with URLs)
# ============================================

@main_routes_bp.route('/class')
@login_required_web
def class_page():
    """Class page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/note')
@login_required_web
def note_page():
    """Note page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/track')
@login_required_web
def track_page():
    """Track page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/pomodoro')
@login_required_web
def pomodoro_page():
    """Pomodoro page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/pomodoro/statistics')
@login_required_web
def pomodoro_statistics_page():
    """Pomodoro statistics page - Direct URL access"""
    return render_template('pomodoro_statistics.html', user=g.user)


@main_routes_bp.route('/setting')
@login_required_web
def setting_page():
    """Setting page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/profile')
@login_required_web
def profile_page():
    """Profile page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/change_password')
@login_required_web
def change_password_page():
    """Change password page - Direct URL access"""
    return render_template('base.html', user=g.user)


@main_routes_bp.route('/dev')
@login_required_web
def dev_page():
    """Dev page - Direct URL access"""
    return render_template('base.html', user=g.user)

