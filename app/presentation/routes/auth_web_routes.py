"""
Simple authentication web routes for register/login functionality.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, flash
from functools import wraps
from ...infrastructure.di.container import get_service
from ...domain.interfaces.services.user_service import UserService
from ...shared.exceptions import NotFoundException, ValidationException, BusinessLogicException

# Create auth web blueprint
auth_web_bp = Blueprint('auth_web', __name__)

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth_web.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_web_bp.before_request
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

@auth_web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user_service = get_service(UserService)
            user = user_service.authenticate_user(email, password)
            session['user_id'] = str(user.id)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('auth_web.dashboard'))
        except (NotFoundException, ValidationException) as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An unexpected error occurred during login.', 'danger')
    
    return render_template('login_page.html')

@auth_web_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user_service = get_service(UserService)
            user_service.register_user(username, email, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth_web.login'))
        except ValidationException as e:
            flash(str(e), 'danger')
        except BusinessLogicException as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An unexpected error occurred during registration.', 'danger')
    
    return render_template('register_page.html')

@auth_web_bp.route('/dashboard')
@login_required_web
def dashboard():
    """Dashboard page"""
    return render_template('dashboard_page.html', user=g.user)

@auth_web_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth_web.login'))

# AJAX endpoints for partial loading
@auth_web_bp.route('/partial/register', methods=['GET', 'POST'])
def partial_register():
    """Register partial for AJAX"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user_service = get_service(UserService)
            user_service.register_user(username, email, password)
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please log in.',
                'redirect': url_for('auth_web.login')
            })
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred during registration.'
            }), 500
    
    # GET request - return register form
    return render_template('register_fragment.html')

@auth_web_bp.route('/partial/login', methods=['GET', 'POST'])
def partial_login():
    """Login partial for AJAX"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user_service = get_service(UserService)
            user = user_service.authenticate_user(email, password)
            session['user_id'] = str(user.id)
            return jsonify({
                'success': True,
                'message': 'Logged in successfully!',
                'redirect': url_for('auth_web.dashboard')
            })
        except (NotFoundException, ValidationException) as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred during login.'
            }), 500
    
    # GET request - return login form
    return render_template('login_fragment.html')
