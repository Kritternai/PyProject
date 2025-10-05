"""
Classwork Detail Routes - Class-specific classwork endpoints
"""

from flask import Blueprint, render_template, request, jsonify, g
from functools import wraps
from flask import session, redirect, url_for

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
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
from ...infrastructure.di.container import container

# Create blueprint
classwork_detail_bp = Blueprint('classwork_detail', __name__, url_prefix='/class')

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

@classwork_detail_bp.route('/<lesson_id>/classwork', methods=['GET'])
def get_classwork_page(lesson_id):
    """Get classwork page for a lesson"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return "Please login first", 401
        
        # Get lesson info (you might want to add lesson service here)
        # For now, we'll just render the template
        return render_template('class_detail/_classwork.html', lesson_id=lesson_id)
    except Exception as e:
        return f"Error loading classwork: {str(e)}", 500

@classwork_detail_bp.route('/<lesson_id>/classwork/tasks', methods=['GET'])
@login_required_web
def get_lesson_tasks(lesson_id):
    """Get all tasks for a lesson"""
    try:
        user_id = g.user.id
        task_service = get_task_service()
        tasks = task_service.get_lesson_tasks(lesson_id, user_id)
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting tasks: {str(e)}'
        }), 500

@classwork_detail_bp.route('/<lesson_id>/classwork/materials', methods=['GET'])
@login_required_web
def get_lesson_materials(lesson_id):
    """Get all materials for a lesson"""
    try:
        user_id = g.user.id
        material_service = get_material_service()
        materials = material_service.get_lesson_materials(lesson_id, user_id)
        
        return jsonify({
            'success': True,
            'materials': [material.to_dict() for material in materials]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting materials: {str(e)}'
        }), 500

@classwork_detail_bp.route('/<lesson_id>/classwork/notes', methods=['GET'])
@login_required_web
def get_lesson_notes(lesson_id):
    """Get all notes for a lesson"""
    try:
        user_id = g.user.id
        note_service = get_note_service()
        notes = note_service.get_lesson_notes(lesson_id, user_id)
        
        return jsonify({
            'success': True,
            'notes': [note.to_dict() for note in notes]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting notes: {str(e)}'
        }), 500

@classwork_detail_bp.route('/<lesson_id>/classwork/dashboard', methods=['GET'])
@login_required_web
def get_lesson_dashboard(lesson_id):
    """Get classwork dashboard for a lesson"""
    try:
        user_id = g.user.id
        
        # Get services
        task_service = get_task_service()
        material_service = get_material_service()
        note_service = get_note_service()
        
        # Get data
        tasks = task_service.get_lesson_tasks(lesson_id, user_id)
        materials = material_service.get_lesson_materials(lesson_id, user_id)
        notes = note_service.get_lesson_notes(lesson_id, user_id)
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status.value == 'done'])
        in_progress_tasks = len([t for t in tasks if t.status.value == 'in_progress'])
        todo_tasks = len([t for t in tasks if t.status.value == 'todo'])
        overdue_tasks = len([t for t in tasks if t.is_overdue()])
        
        return jsonify({
            'success': True,
            'dashboard': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'todo_tasks': todo_tasks,
                'overdue_tasks': overdue_tasks,
                'total_materials': len(materials),
                'total_notes': len(notes),
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting dashboard: {str(e)}'
        }), 500
