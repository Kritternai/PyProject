"""
Routes: Announcement
"""
from flask import Blueprint
from functools import wraps
from flask import session, redirect, url_for, g

from app.presentation.controllers.announcement_controller import get_announcement_controller


def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('register.login'))
        return f(*args, **kwargs)
    return decorated_function

# Create blueprint
announcement_bp = Blueprint('announcement', __name__)

# Get controller
controller = get_announcement_controller()


# ========================================
# ANNOUNCEMENT ROUTES
# ========================================

@announcement_bp.route('/class/<lesson_id>/stream')
@login_required_web
def list_announcements(lesson_id):
    """List all announcements (Stream tab)"""
    return controller.list_announcements(lesson_id)


@announcement_bp.route('/class/<lesson_id>/announcements', methods=['POST'])
@login_required_web
def create_announcement(lesson_id):
    """Create new announcement"""
    return controller.create_announcement(lesson_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>')
@login_required_web
def get_announcement(lesson_id, announcement_id):
    """Get single announcement"""
    return controller.get_announcement(lesson_id, announcement_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>', methods=['PUT'])
@login_required_web
def update_announcement(lesson_id, announcement_id):
    """Update announcement"""
    return controller.update_announcement(lesson_id, announcement_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>', methods=['DELETE'])
@login_required_web
def delete_announcement(lesson_id, announcement_id):
    """Delete announcement"""
    return controller.delete_announcement(lesson_id, announcement_id)


# ========================================
# ANNOUNCEMENT ACTIONS
# ========================================

@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>/pin', methods=['POST'])
@login_required_web
def pin_announcement(lesson_id, announcement_id):
    """Pin announcement to top"""
    return controller.pin_announcement(lesson_id, announcement_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>/unpin', methods=['POST'])
@login_required_web
def unpin_announcement(lesson_id, announcement_id):
    """Unpin announcement"""
    return controller.unpin_announcement(lesson_id, announcement_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>/toggle-comments', methods=['POST'])
@login_required_web
def toggle_comments(lesson_id, announcement_id):
    """Toggle comments on/off"""
    return controller.toggle_comments(lesson_id, announcement_id)


# ========================================
# COMMENT ROUTES
# ========================================

@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>/comments', methods=['POST'])
@login_required_web
def create_comment(lesson_id, announcement_id):
    """Add comment to announcement"""
    return controller.create_comment(lesson_id, announcement_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>/comments/<comment_id>', methods=['PUT'])
@login_required_web
def update_comment(lesson_id, announcement_id, comment_id):
    """Update comment"""
    return controller.update_comment(lesson_id, announcement_id, comment_id)


@announcement_bp.route('/class/<lesson_id>/announcements/<announcement_id>/comments/<comment_id>', methods=['DELETE'])
@login_required_web
def delete_comment(lesson_id, announcement_id, comment_id):
    """Delete comment"""
    return controller.delete_comment(lesson_id, announcement_id, comment_id)

