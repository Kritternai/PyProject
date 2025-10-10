"""
API Routes
General API endpoints for data retrieval
"""

from flask import Blueprint, session, g, jsonify
from ..services import LessonService, NoteService, TaskService

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.before_request
def load_logged_in_user():
    """Load logged in user for API routes"""
    from ..services import UserService
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
# LESSONS DATA API
# ============================================

@api_bp.route('/lessons/data')
def lessons_data():
    """Get lessons data for AJAX"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lessons = lesson_service.get_lessons_by_user(g.user.id)
        return jsonify({
            'success': True,
            'data': [{
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'status': getattr(lesson, 'status', 'not_started'),
                'created_at': lesson.created_at.isoformat() if lesson.created_at else None
            } for lesson in lessons]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# NOTES DATA API
# ============================================

@api_bp.route('/notes/data')
def notes_data():
    """Get notes data for AJAX"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        notes = note_service.get_user_notes(g.user.id)
        return jsonify({
            'success': True,
            'data': [{
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat() if note.created_at else None
            } for note in notes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# TASKS DATA API
# ============================================

@api_bp.route('/tasks/data')
def tasks_data():
    """Get tasks data for AJAX"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        task_service = TaskService()
        tasks = task_service.get_user_tasks(g.user.id)
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# LESSON NOTES API
# ============================================

@api_bp.route('/lessons/<lesson_id>/notes')
def lesson_notes_list(lesson_id):
    """Get notes list for a specific lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        notes = note_service.get_notes_by_user(g.user.id)
        
        # Return HTML fragment
        from flask import render_template
        return render_template('notes_list_fragment.html', notes=notes, user=g.user)
    except Exception as e:
        from flask import render_template
        return render_template('notes_list_fragment.html', notes=[], user=g.user)


@api_bp.route('/lessons/<lesson_id>/notes', methods=['POST'])
def create_lesson_note(lesson_id):
    """Create a note for a specific lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import request
        
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        note_service = NoteService()
        note = note_service.create_note(
            user_id=g.user.id,
            lesson_id=lesson_id,
            title=title,
            content=content
        )
        
        return jsonify({
            'success': True,
            'message': 'Note created successfully',
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/lessons/<lesson_id>/notes/<note_id>')
def get_lesson_note(lesson_id, note_id):
    """Get a specific note for editing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        note = note_service.get_note_by_id(note_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat() if note.created_at else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/lessons/<lesson_id>/notes/<note_id>', methods=['PUT', 'POST'])
def update_lesson_note(lesson_id, note_id):
    """Update a specific note"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from flask import request
        
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        note_service = NoteService()
        note = note_service.update_note(note_id, title=title, content=content)
        
        return jsonify({
            'success': True,
            'message': 'Note updated successfully',
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

