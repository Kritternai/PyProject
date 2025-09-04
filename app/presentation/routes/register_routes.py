"""
Register routes for user registration functionality.
Presentation layer implementation.
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, g, jsonify, flash
from functools import wraps
from ..controllers.register_controller import RegisterController
from ..controllers.login_controller import LoginController
from ..controllers.dashboard_controller import DashboardController

# Create register blueprint
register_bp = Blueprint('register', __name__)

# Initialize controllers
register_controller = RegisterController()
login_controller = LoginController()
dashboard_controller = DashboardController()

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('register.login'))
        return f(*args, **kwargs)
    return decorated_function

@register_bp.before_request
def load_logged_in_user():
    """Load logged in user for web routes"""
    dashboard_controller.load_logged_in_user()

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        return register_controller.register_user_web()
    
    return render_template('register.html')

@register_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        return login_controller.authenticate_user_web()
    
    return render_template('login.html')

@register_bp.route('/dashboard')
@login_required_web
def dashboard():
    """Dashboard page"""
    if not g.user:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('register.login'))
    
    return render_template('base.html', user=g.user)

@register_bp.route('/logout')
def logout():
    """Logout"""
    return login_controller.logout_user()

# AJAX endpoints for partial loading
@register_bp.route('/partial/register', methods=['GET', 'POST'])
def partial_register():
    """Register partial for AJAX"""
    if request.method == 'POST':
        return register_controller.register_user()
    
    # GET request - return register form
    return render_template('register_fragment.html')

@register_bp.route('/partial/login', methods=['GET', 'POST'])
def partial_login():
    """Login partial for AJAX"""
    if request.method == 'POST':
        return login_controller.authenticate_user()
    
    # GET request - return login form
    return render_template('login_fragment.html')

@register_bp.route('/partial/dashboard')
@login_required_web
def partial_dashboard():
    """Dashboard partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dashboard_fragment.html', user=g.user)

# API endpoints
@register_bp.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    return register_controller.register_user()

@register_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    return login_controller.authenticate_user()

@register_bp.route('/api/dashboard', methods=['GET'])
@login_required_web
def api_dashboard():
    """API endpoint for dashboard data"""
    return dashboard_controller.get_dashboard_data()
