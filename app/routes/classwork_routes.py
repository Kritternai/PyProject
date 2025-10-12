"""
Classwork Routes
Routes for classwork task and material management
"""

from flask import Blueprint, request, session, g, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import text
from datetime import datetime
import uuid
import os
from app import db

# Create blueprint
classwork_bp = Blueprint('classwork', __name__, url_prefix='/classwork')


@classwork_bp.before_request
def load_logged_in_user():
    """Load logged in user for classwork routes"""
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


def check_class_permission(lesson_id, user_id, require_owner=False):
    """
    Check if user has permission to access/modify class
    
    Args:
        lesson_id: Class ID
        user_id: User ID to check
        require_owner: If True, only owner has permission
        
    Returns:
        tuple: (has_permission, is_owner)
    """
    from ..services import LessonService
    
    lesson_service = LessonService()
    lesson = lesson_service.get_lesson_by_id(lesson_id)
    
    if not lesson:
        return False, False
    
    is_owner = lesson.user_id == user_id
    
    if require_owner:
        return is_owner, is_owner
    
    # Check if member
    member = db.session.execute(
        text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
        {'lesson_id': lesson_id, 'user_id': user_id}
    ).fetchone()
    
    has_permission = is_owner or (member is not None)
    return has_permission, is_owner


# ============================================
# CLASSWORK DASHBOARD
# ============================================

@classwork_bp.route('/lessons/<lesson_id>/dashboard')
def get_dashboard(lesson_id):
    """Get classwork dashboard for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get task statistics
        stats = db.session.execute(
            text("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tasks,
                    SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as todo_tasks,
                    SUM(CASE WHEN status = 'todo' AND due_date < datetime('now') THEN 1 ELSE 0 END) as overdue_tasks
                FROM classwork_task 
                WHERE lesson_id = :lesson_id AND user_id = :user_id
            """),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        total = stats[0] or 0
        completed = stats[1] or 0
        in_progress = stats[2] or 0
        todo = stats[3] or 0
        overdue = stats[4] or 0
        progress = round((completed / total * 100) if total > 0 else 0, 1)
        
        return jsonify({
            'success': True,
            'data': {
                'lesson_id': lesson_id,
                'total_tasks': total,
                'completed_tasks': completed,
                'in_progress_tasks': in_progress,
                'todo_tasks': todo,
                'overdue_tasks': overdue,
                'progress': progress
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# CLASSWORK TASKS
# ============================================

@classwork_bp.route('/lessons/<lesson_id>/tasks')
def get_tasks(lesson_id):
    """Get classwork tasks for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Check permission
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id)
        if not has_permission:
            return jsonify({'error': 'No permission'}), 403
        
        # Get lesson to find owner
        from ..services import LessonService
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        # Get classwork tasks (shared - created by owner)
        tasks_data = db.session.execute(
            text("""
                SELECT id, title, description, subject, category, priority, status, 
                       due_date, estimated_time, actual_time, created_at, updated_at
                FROM classwork_task 
                WHERE lesson_id = :lesson_id AND user_id = :owner_id
                ORDER BY 
                    CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    due_date ASC,
                    created_at DESC
            """),
            {'lesson_id': lesson_id, 'owner_id': lesson.user_id}
        ).fetchall()
        
        tasks = [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'subject': row[3],
            'category': row[4],
            'priority': row[5],
            'status': row[6],
            'due_date': str(row[7]) if row[7] else None,
            'estimated_time': row[8],
            'actual_time': row[9],
            'created_at': str(row[10]) if row[10] else None,
            'updated_at': str(row[11]) if row[11] else None
        } for row in tasks_data]
        
        return jsonify({
            'success': True,
            'data': tasks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@classwork_bp.route('/lessons/<lesson_id>/tasks', methods=['POST'])
def create_task(lesson_id):
    """Create a new classwork task (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Check permission - only owner can create
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can create tasks'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Insert task into database
        db.session.execute(
            text("""
                INSERT INTO classwork_task 
                (id, user_id, lesson_id, title, description, subject, category, 
                 priority, status, due_date, estimated_time, created_at, updated_at)
                VALUES 
                (:id, :user_id, :lesson_id, :title, :description, :subject, :category,
                 :priority, :status, :due_date, :estimated_time, :created_at, :updated_at)
            """),
            {
                'id': task_id,
                'user_id': g.user.id,
                'lesson_id': lesson_id,
                'title': data.get('title'),
                'description': data.get('description', ''),
                'subject': data.get('subject', ''),
                'category': data.get('category', ''),
                'priority': data.get('priority', 'medium'),
                'status': data.get('status', 'todo'),
                'due_date': data.get('due_date'),
                'estimated_time': data.get('estimated_time', 0),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'data': {
                'id': task_id,
                'title': data.get('title'),
                'status': data.get('status', 'todo')
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@classwork_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a classwork task (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get task to find lesson_id
        task_data = db.session.execute(
            text("SELECT lesson_id FROM classwork_task WHERE id = :task_id"),
            {'task_id': task_id}
        ).fetchone()
        
        if not task_data:
            return jsonify({'error': 'Task not found'}), 404
        
        lesson_id = task_data[0]
        
        # Check permission - only owner can update
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can update tasks'}), 403
        
        data = request.get_json()
        
        # Build update query dynamically
        update_fields = []
        params = {'id': task_id, 'updated_at': datetime.now()}
        
        for field in ['title', 'description', 'subject', 'category', 'priority', 
                      'status', 'due_date', 'estimated_time', 'actual_time']:
            if field in data:
                update_fields.append(f'{field} = :{field}')
                params[field] = data[field]
        
        update_fields.append('updated_at = :updated_at')
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Execute update
        result = db.session.execute(
            text(f"""
                UPDATE classwork_task 
                SET {', '.join(update_fields)}
                WHERE id = :id
            """),
            params
        )
        db.session.commit()
        
        if result.rowcount == 0:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@classwork_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a classwork task (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get task to find lesson_id
        task_data = db.session.execute(
            text("SELECT lesson_id FROM classwork_task WHERE id = :task_id"),
            {'task_id': task_id}
        ).fetchone()
        
        if not task_data:
            return jsonify({'error': 'Task not found'}), 404
        
        lesson_id = task_data[0]
        
        # Check permission - only owner can delete
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can delete tasks'}), 403
        
        result = db.session.execute(
            text("""
                DELETE FROM classwork_task 
                WHERE id = :id
            """),
            {'id': task_id}
        )
        db.session.commit()
        
        if result.rowcount == 0:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================
# CLASSWORK MATERIALS
# ============================================

@classwork_bp.route('/lessons/<lesson_id>/materials')
def get_materials(lesson_id):
    """Get classwork materials for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Check permission
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id)
        if not has_permission:
            return jsonify({'error': 'No permission'}), 403
        
        # Get lesson to find owner
        from ..services import LessonService
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        # Get classwork materials (shared - created by owner)
        materials_data = db.session.execute(
            text("""
                SELECT id, title, description, file_path, file_type, file_size,
                       subject, category, tags, created_at, updated_at
                FROM classwork_material 
                WHERE lesson_id = :lesson_id AND user_id = :owner_id
                ORDER BY created_at DESC
            """),
            {'lesson_id': lesson_id, 'owner_id': lesson.user_id}
        ).fetchall()
        
        materials = [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'file_path': row[3],
            'file_name': row[3].split('/')[-1] if row[3] else '',
            'file_type': row[4],
            'file_size': row[5],
            'subject': row[6],
            'category': row[7],
            'tags': row[8],
            'created_at': str(row[9]) if row[9] else None,
            'updated_at': str(row[10]) if row[10] else None
        } for row in materials_data]
        
        return jsonify({
            'success': True,
            'data': materials
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@classwork_bp.route('/lessons/<lesson_id>/materials', methods=['POST'])
def create_material(lesson_id):
    """Create a new classwork material (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Check permission - only owner can create
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can create materials'}), 403
        # Check if file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Secure filename and save
            filename = secure_filename(file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            materials_folder = os.path.join(upload_folder, 'classwork', lesson_id)
            os.makedirs(materials_folder, exist_ok=True)
            
            file_path = os.path.join(materials_folder, filename)
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            
            # Get form data
            title = request.form.get('title', filename)
            description = request.form.get('description', '')
            subject = request.form.get('subject', '')
            category = request.form.get('category', '')
            tags = request.form.get('tags', '')
        else:
            # JSON data without file
            data = request.get_json()
            title = data.get('title')
            if not title:
                return jsonify({'error': 'Title is required'}), 400
            
            description = data.get('description', '')
            subject = data.get('subject', '')
            category = data.get('category', '')
            tags = data.get('tags', '')
            file_path = data.get('file_path', '')
            file_type = data.get('file_type', '')
            file_size = data.get('file_size', 0)
        
        # Generate material ID
        material_id = str(uuid.uuid4())
        
        # Insert material into database
        db.session.execute(
            text("""
                INSERT INTO classwork_material 
                (id, user_id, lesson_id, title, description, file_path, file_type, file_size,
                 subject, category, tags, created_at, updated_at)
                VALUES 
                (:id, :user_id, :lesson_id, :title, :description, :file_path, :file_type, :file_size,
                 :subject, :category, :tags, :created_at, :updated_at)
            """),
            {
                'id': material_id,
                'user_id': g.user.id,
                'lesson_id': lesson_id,
                'title': title,
                'description': description,
                'file_path': file_path,
                'file_type': file_type,
                'file_size': file_size,
                'subject': subject,
                'category': category,
                'tags': tags,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Material created successfully',
            'data': {
                'id': material_id,
                'title': title,
                'file_type': file_type
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@classwork_bp.route('/materials/<material_id>', methods=['DELETE'])
def delete_material(material_id):
    """Delete a classwork material (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get material to find lesson_id
        material_data = db.session.execute(
            text("SELECT lesson_id, file_path FROM classwork_material WHERE id = :id"),
            {'id': material_id}
        ).fetchone()
        
        if not material_data:
            return jsonify({'error': 'Material not found'}), 404
        
        lesson_id = material_data[0]
        file_path = material_data[1]
        
        # Check permission - only owner can delete
        has_permission, is_owner = check_class_permission(lesson_id, g.user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can delete materials'}), 403
        
        # Delete from database
        db.session.execute(
            text("""
                DELETE FROM classwork_material 
                WHERE id = :id
            """),
            {'id': material_id}
        )
        db.session.commit()
        
        # Delete file if exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore file deletion errors
        
        return jsonify({
            'success': True,
            'message': 'Material deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================
# CLASSWORK COMBINED DATA
# ============================================

@classwork_bp.route('/lessons/<lesson_id>')
def get_classwork(lesson_id):
    """Get all classwork content for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from ..services import LessonService
        
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        # Get classwork tasks
        classwork_tasks = db.session.execute(
            text("""
                SELECT id, title, description, subject, category, priority, status, 
                       due_date, estimated_time, actual_time, created_at, updated_at
                FROM classwork_task 
                WHERE lesson_id = :lesson_id AND user_id = :user_id
                ORDER BY created_at DESC
            """),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchall()
        
        # Get classwork materials
        classwork_materials = db.session.execute(
            text("""
                SELECT id, title, description, file_path, file_type, file_size,
                       subject, category, tags, created_at, updated_at
                FROM classwork_material 
                WHERE lesson_id = :lesson_id AND user_id = :user_id
                ORDER BY created_at DESC
            """),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchall()
        
        # Convert to list of dicts
        tasks = [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'subject': row[3],
            'category': row[4],
            'priority': row[5],
            'status': row[6],
            'due_date': row[7],
            'estimated_time': row[8],
            'actual_time': row[9],
            'created_at': row[10],
            'updated_at': row[11]
        } for row in classwork_tasks]
        
        materials = [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'file_path': row[3],
            'file_name': row[3].split('/')[-1] if row[3] else '',
            'file_type': row[4],
            'file_size': row[5],
            'subject': row[6],
            'category': row[7],
            'tags': row[8],
            'created_at': row[9],
            'updated_at': row[10]
        } for row in classwork_materials]
        
        return jsonify({
            'success': True,
            'data': {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'classwork': {
                    'tasks': tasks,
                    'materials': materials
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

