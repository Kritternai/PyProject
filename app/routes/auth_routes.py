"""
Authentication routes for MVC architecture.
"""
from flask import Blueprint
from ..views.auth_views import AuthController

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize controller
auth_controller = AuthController()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint"""
    return auth_controller.login()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register endpoint"""
    return auth_controller.register()

@auth_bp.route('/logout')
def logout():
    """Logout endpoint"""
    return auth_controller.logout()
