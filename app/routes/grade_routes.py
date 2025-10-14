"""
Grade Routes - HTTP endpoints for grade management
Handles routing and delegates business logic to GradeController
"""

from flask import Blueprint, render_template, request, jsonify, session, g
from functools import wraps
from ..controllers.grade_views import GradeController
from ..middleware.auth_middleware import login_required
from app.utils.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException
)
from app import db
from sqlalchemy import text

# Create blueprint
grade_bp = Blueprint('grades', __name__, url_prefix='/grades')


def check_g_user():
    """Check if g.user is available and return user or error response"""
    if not hasattr(g, 'user') or not g.user:
        return None, jsonify({'error': 'User not found'}), 401
    return g.user, None, None

def check_class_permission(lesson_id, user_id, require_owner=False):
    """Check if user has permission to access/modify class"""
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


@grade_bp.before_request
def load_logged_in_user():
    """Load logged in user for grade routes"""
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
    
    # Ensure g.user is always defined
    if not hasattr(g, 'user'):
        g.user = None


# ==========================================
# GRADE CONFIGURATION
# ==========================================

@grade_bp.route('/lessons/<lesson_id>/config', methods=['GET'])
def get_grade_config(lesson_id):
    """Get grade configuration for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        config = GradeController.get_grade_config(lesson_id)
        return jsonify({
            'success': True,
            'data': config
        })
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/config', methods=['POST'])
def create_grade_config(lesson_id):
    """Create grade configuration (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if g.user is available
    user, error_response, status_code = check_g_user()
    if error_response:
        return error_response, status_code
    
    try:
        # Check permission - only owner can create config
        has_permission, is_owner = check_class_permission(lesson_id, user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can create grade configuration'}), 403
        
        data = request.get_json()
        
        if not data or 'grading_scale' not in data:
            return jsonify({'error': 'Grading scale is required'}), 400
        
        config = GradeController.create_grade_config(
            lesson_id=lesson_id,
            grading_scale=data['grading_scale'],
            grading_type=data.get('grading_type', 'percentage'),
            total_points=data.get('total_points', 100),
            passing_grade=data.get('passing_grade', 'D'),
            passing_percentage=data.get('passing_percentage', 50.0)
        )
        
        return jsonify({
            'success': True,
            'message': 'Grade configuration saved successfully',
            'data': {
                'id': config.id,
                'lesson_id': config.lesson_id
            }
        }), 201
        
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/config', methods=['PUT'])
def update_grade_config(lesson_id):
    """Update grade configuration"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        if not data or 'grading_scale' not in data:
            return jsonify({'error': 'Grading scale is required'}), 400
        
        config = GradeController.update_grade_config(
            lesson_id=lesson_id,
            grading_scale=data['grading_scale'],
            grading_type=data.get('grading_type'),
            total_points=data.get('total_points'),
            passing_grade=data.get('passing_grade'),
            passing_percentage=data.get('passing_percentage')
        )
        
        return jsonify({
            'success': True,
            'message': 'Grade configuration updated successfully'
        })
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/config', methods=['DELETE'])
def delete_grade_config(lesson_id):
    """Delete grade configuration and all related data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        GradeController.delete_grade_config(lesson_id)
        
        return jsonify({
            'success': True,
            'message': 'Grade configuration deleted successfully'
        })
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# GRADE CATEGORIES
# ==========================================

@grade_bp.route('/lessons/<lesson_id>/categories', methods=['GET'])
def get_categories(lesson_id):
    """Get all grade categories for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        categories = GradeController.get_categories(lesson_id)
        
        categories_data = [{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'weight': float(cat.weight),
            'color': cat.color,
            'icon': cat.icon,
            'order_index': cat.order_index
        } for cat in categories]
        
        return jsonify({
            'success': True,
            'data': categories_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/categories', methods=['POST'])
def create_category(lesson_id):
    """Create a new grade category (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if g.user is available
    user, error_response, status_code = check_g_user()
    if error_response:
        return error_response, status_code
    
    try:
        # Check permission - only owner can create category
        has_permission, is_owner = check_class_permission(lesson_id, user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can create categories'}), 403
        
        data = request.get_json()
        
        if not data or 'name' not in data or 'weight' not in data:
            return jsonify({'error': 'Name and weight are required'}), 400
        
        category = GradeController.create_category(
            lesson_id=lesson_id,
            name=data['name'],
            weight=float(data['weight']),
            description=data.get('description', ''),
            color=data.get('color', '#3B82F6'),
            icon=data.get('icon', 'bi-clipboard'),
            order_index=data.get('order_index', 0)
        )
        
        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'data': {
                'id': category.id,
                'name': category.name,
                'weight': float(category.weight)
            }
        }), 201
        
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a grade category"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        GradeController.delete_category(category_id)
        
        return jsonify({
            'success': True,
            'message': 'Category deleted successfully'
        })
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# GRADE ITEMS
# ==========================================

@grade_bp.route('/lessons/<lesson_id>/items', methods=['GET'])
def get_grade_items(lesson_id):
    """Get all grade items for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        items = GradeController.get_grade_items(lesson_id)
        
        items_data = [{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'points_possible': float(item.points_possible),
            'due_date': item.due_date.isoformat() if item.due_date else None,
            'is_published': item.is_published,
            'category_id': item.category_id
        } for item in items]
        
        return jsonify({
            'success': True,
            'data': items_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/items', methods=['POST'])
def create_grade_item(lesson_id):
    """Create a new grade item (Owner only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if g.user is available
    user, error_response, status_code = check_g_user()
    if error_response:
        return error_response, status_code
    
    try:
        # Check permission - only owner can create items
        has_permission, is_owner = check_class_permission(lesson_id, user.id, require_owner=True)
        if not is_owner:
            return jsonify({'error': 'Only owner can create grade items'}), 403
        
        data = request.get_json()
        
        if not data or 'name' not in data or 'category_id' not in data or 'points_possible' not in data:
            return jsonify({'error': 'Name, category_id, and points_possible are required'}), 400
        
        item = GradeController.create_grade_item(
            lesson_id=lesson_id,
            category_id=data['category_id'],
            name=data['name'],
            points_possible=float(data['points_possible']),
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            is_published=data.get('is_published', False),
            classwork_task_id=data.get('classwork_task_id')  # Link to task
        )
        
        # Auto-generate activity
        try:
            from ..controllers.stream_views import StreamController
            from flask import g
            stream_controller = StreamController()
            stream_controller.create_activity(
                lesson_id=lesson_id,
                user_id=user.id,
                activity_type='grade_added',
                title=f'{user.name} added grade item: {data["name"]}'
            )
        except Exception as e:
            print(f"Warning: Failed to create activity: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Grade item created successfully',
            'data': {
                'id': item.id,
                'name': item.name,
                'points_possible': float(item.points_possible),
                'classwork_task_id': item.classwork_task_id
            }
        }), 201
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/available-tasks', methods=['GET'])
def get_available_tasks(lesson_id):
    """Get classwork tasks that can be linked to grade items"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        tasks = GradeController.get_available_tasks(lesson_id)
        
        return jsonify({
            'success': True,
            'data': tasks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/items/<item_id>', methods=['PUT'])
def update_grade_item(item_id):
    """Update a grade item"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        # Add user_id for score updates
        data['user_id'] = user_id
        
        item = GradeController.update_grade_item(item_id, **data)
        
        return jsonify({
            'success': True, 
            'message': 'Grade item updated successfully',
            'data': {
                'id': item.id,
                'name': item.name,
                'points_possible': float(item.points_possible),
                'due_date': item.due_date.isoformat() if item.due_date else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# STUDENT GRADES
# ==========================================

@grade_bp.route('/lessons/<lesson_id>/my-grades', methods=['GET'])
def get_my_grades(lesson_id):
    """Get all grades for current student"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if g.user is available
    user, error_response, status_code = check_g_user()
    if error_response:
        return error_response, status_code
    
    try:
        # Check permission - owner or member can view their grades
        has_permission, is_owner = check_class_permission(lesson_id, user.id)
        if not has_permission:
            return jsonify({'error': 'No permission'}), 403
        
        grades = GradeController.get_student_grades(lesson_id, user.id)
        
        return jsonify({
            'success': True,
            'data': grades
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/summary', methods=['GET'])
def get_grade_summary(lesson_id):
    """Get grade summary with goals"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if g.user is available
    user, error_response, status_code = check_g_user()
    if error_response:
        return error_response, status_code
    
    try:
        # Check permission - owner or member can view summary
        has_permission, is_owner = check_class_permission(lesson_id, user.id)
        if not has_permission:
            return jsonify({'error': 'No permission'}), 403
        
        summary = GradeController.calculate_grade_summary(lesson_id, user.id)
        
        if 'error' in summary:
            return jsonify(summary), 404
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# SUBMIT GRADES (Teacher/Self-grading)
# ==========================================

@grade_bp.route('/items/<grade_item_id>/submit', methods=['POST'])
def submit_grade(grade_item_id):
    """Submit a grade for a student"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        if 'score' not in data:
            return jsonify({'error': 'Score is required'}), 400
        
        # Check if g.user is available
        user, error_response, status_code = check_g_user()
        if error_response:
            return error_response, status_code
        
        entry = GradeController.submit_grade(
            grade_item_id=grade_item_id,
            user_id=user.id,  # Self-grading for now
            score=float(data['score']),
            comments=data.get('comments'),
            is_late=data.get('is_late', False),
            late_penalty=data.get('late_penalty', 0)
        )
        
        return jsonify({
            'success': True,
            'message': 'Grade submitted successfully',
            'data': {
                'entry_id': entry.id,
                'score': float(entry.score),
                'percentage': entry.percentage
            }
        })
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# CALCULATORS
# ==========================================

@grade_bp.route('/lessons/<lesson_id>/goal-calculator', methods=['POST'])
def calculate_goal(lesson_id):
    """Calculate what score is needed to achieve target grade"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        if not data or 'target_grade' not in data:
            return jsonify({'error': 'Target grade is required'}), 400
        
        # Check if g.user is available
        user, error_response, status_code = check_g_user()
        if error_response:
            return error_response, status_code
        
        result = GradeController.calculate_goal(
            lesson_id=lesson_id,
            user_id=user.id,
            target_grade=data['target_grade']
        )
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
    except ValidationException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@grade_bp.route('/lessons/<lesson_id>/what-if', methods=['POST'])
def calculate_what_if(lesson_id):
    """Calculate what-if scenario with hypothetical scores"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        if not data or 'hypothetical_scores' not in data:
            return jsonify({'error': 'Hypothetical scores are required'}), 400
        
        # Check if g.user is available
        user, error_response, status_code = check_g_user()
        if error_response:
            return error_response, status_code
        
        result = GradeController.calculate_what_if(
            lesson_id=lesson_id,
            user_id=user.id,
            hypothetical_scores=data['hypothetical_scores']
        )
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# HTML FRAGMENTS (for SPA)
# ==========================================

@grade_bp.route('/partial/class/<lesson_id>/grades')
def partial_grades(lesson_id):
    """HTML fragment for grades tab in SPA"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from ..services import LessonService
        from app import db
        from sqlalchemy import text
        
        # Get lesson
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return '<div class="alert alert-danger">Class not found.</div>', 404
        
        # Check if g.user is available
        user, error_response, status_code = check_g_user()
        if error_response:
            return error_response, status_code
        
        # Check permission: must be owner or member
        is_owner = lesson.user_id == user.id
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': user.id}
        ).fetchone()
        
        if not is_owner and not member:
            return '<div class="alert alert-danger">You do not have permission to view this class.</div>', 403
        
        return render_template('class_detail/_grades.html', 
                             lesson_id=lesson_id,
                             user=g.user,
                             is_owner=is_owner)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading grades: {str(e)}</div>', 500


@grade_bp.route('/test-api')
def test_api():
    """Test page for debugging grades API"""
    return render_template('test_grades_api.html')

