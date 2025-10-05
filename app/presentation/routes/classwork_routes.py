"""
Classwork Routes - API Endpoints
"""

from flask import Blueprint, request, jsonify, g, session
from functools import wraps

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function
from ...application.services.classwork_service import (
    ClassworkTaskService,
    ClassworkMaterialService,
    ClassworkNoteService
)
from ...infrastructure.database.classwork_repository import (
    ClassworkTaskRepositoryImpl,
    ClassworkMaterialRepositoryImpl,
    ClassworkNoteRepositoryImpl
)
from ...presentation.controllers.classwork_controller import (
    ClassworkTaskController,
    ClassworkMaterialController,
    ClassworkNoteController
)
from ...infrastructure.di.container import container

# Create blueprint
classwork_bp = Blueprint('classwork', __name__, url_prefix='/classwork')

# Initialize services
def get_task_service():
    """Get task service instance"""
    from ... import db
    task_repository = ClassworkTaskRepositoryImpl(db)
    return ClassworkTaskService(task_repository)

def get_material_service():
    """Get material service instance"""
    from ... import db
    material_repository = ClassworkMaterialRepositoryImpl(db)
    return ClassworkMaterialService(material_repository)

def get_note_service():
    """Get note service instance"""
    from ... import db
    note_repository = ClassworkNoteRepositoryImpl(db)
    return ClassworkNoteService(note_repository)

# Initialize controllers
task_controller = ClassworkTaskController(get_task_service())
material_controller = ClassworkMaterialController(get_material_service())
note_controller = ClassworkNoteController(get_note_service())

# Task Routes
@classwork_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new classwork task"""
    return task_controller.create_task()

@classwork_bp.route('/tasks/<task_id>', methods=['GET'])
@login_required_web
def get_task(task_id):
    """Get task by ID"""
    return task_controller.get_task(task_id)

@classwork_bp.route('/tasks/<task_id>', methods=['PUT'])
@login_required_web
def update_task(task_id):
    """Update task"""
    return task_controller.update_task(task_id)

@classwork_bp.route('/tasks/<task_id>', methods=['DELETE'])
@login_required_web
def delete_task(task_id):
    """Delete task"""
    return task_controller.delete_task(task_id)

@classwork_bp.route('/tasks/<task_id>/complete', methods=['POST'])
@login_required_web
def mark_task_complete(task_id):
    """Mark task as complete"""
    return task_controller.mark_task_complete(task_id)

@classwork_bp.route('/tasks/search', methods=['GET'])
@login_required_web
def search_tasks():
    """Search tasks"""
    return task_controller.search_tasks()

@classwork_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get classwork dashboard for all lessons"""
    return task_controller.get_dashboard()

@classwork_bp.route('/lessons/<lesson_id>/dashboard', methods=['GET'])
def get_lesson_dashboard(lesson_id):
    """Get classwork dashboard for a specific lesson"""
    return task_controller.get_dashboard(lesson_id)

@classwork_bp.route('/lessons/<lesson_id>/tasks', methods=['GET'])
def get_lesson_tasks(lesson_id):
    """Get all tasks for a lesson"""
    return task_controller.get_lesson_tasks(lesson_id)

# Material Routes
@classwork_bp.route('/materials', methods=['POST'])
def create_material():
    """Create a new classwork material"""
    return material_controller.create_material()

@classwork_bp.route('/materials/<material_id>', methods=['GET'])
@login_required_web
def get_material(material_id):
    """Get material by ID"""
    return material_controller.get_material(material_id)

@classwork_bp.route('/materials/<material_id>', methods=['PUT'])
@login_required_web
def update_material(material_id):
    """Update material"""
    return material_controller.update_material(material_id)

@classwork_bp.route('/materials/<material_id>', methods=['DELETE'])
@login_required_web
def delete_material(material_id):
    """Delete material"""
    return material_controller.delete_material(material_id)

@classwork_bp.route('/materials/search', methods=['GET'])
@login_required_web
def search_materials():
    """Search materials"""
    return material_controller.search_materials()

@classwork_bp.route('/lessons/<lesson_id>/materials', methods=['GET'])
def get_lesson_materials(lesson_id):
    """Get all materials for a lesson"""
    return material_controller.get_lesson_materials(lesson_id)

# Note Routes
@classwork_bp.route('/notes', methods=['POST'])
@login_required_web
def create_note():
    """Create a new classwork note"""
    return note_controller.create_note()

@classwork_bp.route('/notes/<note_id>', methods=['GET'])
@login_required_web
def get_note(note_id):
    """Get note by ID"""
    return note_controller.get_note(note_id)

@classwork_bp.route('/notes/<note_id>', methods=['PUT'])
@login_required_web
def update_note(note_id):
    """Update note"""
    return note_controller.update_note(note_id)

@classwork_bp.route('/notes/<note_id>', methods=['DELETE'])
@login_required_web
def delete_note(note_id):
    """Delete note"""
    return note_controller.delete_note(note_id)

@classwork_bp.route('/notes/search', methods=['GET'])
@login_required_web
def search_notes():
    """Search notes"""
    return note_controller.search_notes()

@classwork_bp.route('/lessons/<lesson_id>/notes', methods=['GET'])
@login_required_web
def get_lesson_notes(lesson_id):
    """Get all notes for a lesson"""
    return note_controller.get_lesson_notes(lesson_id)

# Dashboard Routes

# Statistics Routes
@classwork_bp.route('/stats', methods=['GET'])
@login_required_web
def get_stats():
    """Get classwork statistics"""
    try:
        user_id = g.user.id
        
        # Get services
        task_service = get_task_service()
        material_service = get_material_service()
        note_service = get_note_service()
        
        # Get all data
        all_tasks = task_service.get_lesson_tasks('', user_id)
        all_materials = material_service.get_lesson_materials('', user_id)
        all_notes = material_service.get_lesson_materials('', user_id)
        
        # Calculate statistics
        stats = {
            'tasks': {
                'total': len(all_tasks),
                'completed': len([t for t in all_tasks if t.status.value == 'done']),
                'in_progress': len([t for t in all_tasks if t.status.value == 'in_progress']),
                'todo': len([t for t in all_tasks if t.status.value == 'todo']),
                'overdue': len(task_service.get_overdue_tasks(user_id))
            },
            'materials': {
                'total': len(all_materials),
                'by_type': {}
            },
            'notes': {
                'total': len(all_notes),
                'by_subject': {}
            }
        }
        
        # Calculate materials by type
        for material in all_materials:
            material_type = material.file_type.value if material.file_type else 'other'
            stats['materials']['by_type'][material_type] = stats['materials']['by_type'].get(material_type, 0) + 1
        
        # Calculate notes by subject
        for note in all_notes:
            subject = note.subject or 'Uncategorized'
            stats['notes']['by_subject'][subject] = stats['notes']['by_subject'].get(subject, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting stats: {str(e)}'
        }), 500
