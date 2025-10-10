"""
Lesson routes following Clean Architecture principles.
Defines HTTP endpoints for lesson operations.
"""

from flask import Blueprint
from ..controllers.lesson_views import LessonController
from ..middleware.auth_middleware import login_required

# Create blueprint
lesson_bp = Blueprint('lesson', __name__, url_prefix='/api/lessons')

# Initialize controller
lesson_controller = LessonController()


@lesson_bp.route('', methods=['POST'])
@login_required
def create_lesson():
    """Create a new lesson."""
    return lesson_controller.create_lesson()


@lesson_bp.route('/<lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    """Get lesson by ID."""
    return lesson_controller.get_lesson(lesson_id)


@lesson_bp.route('', methods=['GET'])
@login_required
def get_user_lessons():
    """Get lessons for current user."""
    return lesson_controller.get_user_lessons()


@lesson_bp.route('/<lesson_id>', methods=['PUT'])
@login_required
def update_lesson(lesson_id):
    """Update lesson."""
    return lesson_controller.update_lesson(lesson_id)


@lesson_bp.route('/<lesson_id>', methods=['DELETE'])
@login_required
def delete_lesson(lesson_id):
    """Delete lesson."""
    return lesson_controller.delete_lesson(lesson_id)


@lesson_bp.route('/<lesson_id>/status', methods=['PUT'])
@login_required
def change_lesson_status(lesson_id):
    """Change lesson status."""
    return lesson_controller.change_lesson_status(lesson_id)


@lesson_bp.route('/<lesson_id>/progress', methods=['PUT'])
@login_required
def update_lesson_progress(lesson_id):
    """Update lesson progress."""
    return lesson_controller.update_lesson_progress(lesson_id)


@lesson_bp.route('/<lesson_id>/favorite', methods=['PUT'])
@login_required
def toggle_favorite(lesson_id):
    """Toggle lesson favorite status."""
    return lesson_controller.toggle_favorite(lesson_id)


@lesson_bp.route('/search', methods=['GET'])
@login_required
def search_lessons():
    """Search lessons."""
    return lesson_controller.search_lessons()


@lesson_bp.route('/statistics', methods=['GET'])
@login_required
def get_lesson_statistics():
    """Get lesson statistics."""
    return lesson_controller.get_lesson_statistics()
