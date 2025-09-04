"""
Authentication routes following Clean Architecture principles.
Defines HTTP endpoints for authentication operations.
"""

from flask import Blueprint
from ..controllers.auth_controller import AuthController

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize controller
auth_controller = AuthController()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login user."""
    return auth_controller.login()


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user."""
    return auth_controller.logout()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user."""
    return auth_controller.register()


@auth_bp.route('/status', methods=['GET'])
def check_auth_status():
    """Check authentication status."""
    return auth_controller.check_auth_status()
