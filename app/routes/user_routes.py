"""
User routes following Clean Architecture principles.
Defines HTTP endpoints for user operations.
"""

from flask import Blueprint
from ..controllers.user_views import UserController
from ..middleware import login_required

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/users')

# Initialize controller
user_controller = UserController()


@user_bp.route('', methods=['POST'])
def create_user():
    """Create a new user."""
    return user_controller.create_user()


@user_bp.route('/<user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get user by ID."""
    return user_controller.get_user(user_id)


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_current_user_profile():
    """Get current user's profile."""
    return user_controller.get_current_user_profile()


@user_bp.route('/<user_id>/profile', methods=['PUT'])
@login_required
def update_user_profile(user_id):
    """Update user profile."""
    return user_controller.update_user_profile(user_id)


@user_bp.route('/<user_id>/password', methods=['PUT'])
@login_required
def change_password(user_id):
    """Change user password."""
    return user_controller.change_password(user_id)


@user_bp.route('', methods=['GET'])
@login_required
def get_users():
    """Get all users (admin only)."""
    return user_controller.get_users()


@user_bp.route('/search', methods=['GET'])
@login_required
def search_users():
    """Search users (admin only)."""
    return user_controller.search_users()


@user_bp.route('/<user_id>/statistics', methods=['GET'])
@login_required
def get_user_statistics(user_id):
    """Get user statistics."""
    return user_controller.get_user_statistics(user_id)


@user_bp.route('/current/profile', methods=['PUT'])
@login_required  
def update_current_user_profile():
    """Update current user's profile."""
    return user_controller.update_current_user_profile()


@user_bp.route('/current/export', methods=['GET'])
@login_required
def export_current_user_data():
    """Export current user's data."""
    return user_controller.export_current_user_data()
