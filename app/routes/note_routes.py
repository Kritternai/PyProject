"""
Note routes following Clean Architecture principles.
Defines HTTP endpoints for note operations.
"""

from flask import Blueprint
from ..views.note_views import NoteController
from ..middleware.auth_middleware import login_required
# from ..middleware.rate_limiter import rate_limit, strict_rate_limit

# Create blueprint
note_bp = Blueprint('note', __name__, url_prefix='/api/notes')

# Initialize controller
note_controller = NoteController()


@note_bp.route('', methods=['POST'])
@login_required
# @rate_limit(user_limit=10, ip_limit=20, window=5)
def create_note():
    """Create a new note."""
    return note_controller.create_note()


@note_bp.route('/<note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """Get note by ID."""
    return note_controller.get_note(note_id)


@note_bp.route('', methods=['GET'])
@login_required
def get_user_notes():
    """Get notes for current user."""
    return note_controller.get_user_notes()


@note_bp.route('/<note_id>', methods=['PUT'])
@login_required
# @rate_limit(user_limit=10, ip_limit=20, window=5)
def update_note(note_id):
    """Update note."""
    return note_controller.update_note(note_id)


@note_bp.route('/<note_id>', methods=['DELETE'])
@login_required
# @strict_rate_limit(user_limit=5, ip_limit=10, window=5)
def delete_note(note_id):
    """Delete note."""
    return note_controller.delete_note(note_id)


@note_bp.route('/lesson/<lesson_id>', methods=['GET'])
@login_required
def get_notes_by_lesson(lesson_id):
    """Get notes for a specific lesson."""
    return note_controller.get_notes_by_lesson(lesson_id)


@note_bp.route('/section/<section_id>', methods=['GET'])
@login_required
def get_notes_by_section(section_id):
    """Get notes for a specific section."""
    return note_controller.get_notes_by_section(section_id)


@note_bp.route('/search', methods=['GET'])
@login_required
def search_notes():
    """Search notes."""
    return note_controller.search_notes()


@note_bp.route('/search/tags', methods=['GET'])
@login_required
def search_notes_by_tags():
    """Search notes by tags."""
    return note_controller.search_notes_by_tags()


@note_bp.route('/public', methods=['GET'])
def get_public_notes():
    """Get public notes."""
    return note_controller.get_public_notes()


@note_bp.route('/<note_id>/public', methods=['PUT'])
@login_required
def toggle_public_status(note_id):
    """Toggle note public status."""
    return note_controller.toggle_public_status(note_id)


@note_bp.route('/<note_id>/tags', methods=['POST'])
@login_required
def add_tag(note_id):
    """Add tag to note."""
    return note_controller.add_tag(note_id)


@note_bp.route('/<note_id>/tags', methods=['DELETE'])
@login_required
def remove_tag(note_id):
    """Remove tag from note."""
    return note_controller.remove_tag(note_id)


@note_bp.route('/statistics', methods=['GET'])
@login_required
def get_note_statistics():
    """Get note statistics."""
    return note_controller.get_note_statistics()


@note_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_notes():
    """Get recent notes."""
    return note_controller.get_recent_notes()


@note_bp.route('/most-viewed', methods=['GET'])
@login_required
def get_most_viewed_notes():
    """Get most viewed notes."""
    return note_controller.get_most_viewed_notes()


@note_bp.route('/tags', methods=['GET'])
@login_required
def get_all_user_tags():
    """Get all unique tags for user."""
    return note_controller.get_all_user_tags()
