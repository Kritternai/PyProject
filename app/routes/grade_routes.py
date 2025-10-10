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

# Create blueprint
grade_bp = Blueprint('grades', __name__, url_prefix='/grades')


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


@grade_bp.route('/lessons/<lesson_id>/config', methods=['POST', 'PUT'])
def save_grade_config(lesson_id):
    """Create or update grade configuration"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
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
    """Create a new grade category"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'weight' not in data:
            return jsonify({'error': 'Name and weight are required'}), 400
        
        category = GradeController.create_category(
            lesson_id=lesson_id,
            name=data['name'],
            weight=float(data['weight']),
            description=data.get('description', ''),
            color=data.get('color', '#3B82F6'),
            icon=data.get('icon', 'bi-clipboard')
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
    """Create a new grade item"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
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
            is_published=data.get('is_published', False)
        )
        
        return jsonify({
            'success': True,
            'message': 'Grade item created successfully',
            'data': {
                'id': item.id,
                'name': item.name,
                'points_possible': float(item.points_possible)
            }
        }), 201
        
    except NotFoundException as e:
        return jsonify({'error': str(e)}), 404
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
    
    try:
        grades = GradeController.get_student_grades(lesson_id, g.user.id)
        
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
    
    try:
        summary = GradeController.calculate_grade_summary(lesson_id, g.user.id)
        
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
        
        entry = GradeController.submit_grade(
            grade_item_id=grade_item_id,
            user_id=g.user.id,  # Self-grading for now
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
        
        result = GradeController.calculate_goal(
            lesson_id=lesson_id,
            user_id=g.user.id,
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
        
        result = GradeController.calculate_what_if(
            lesson_id=lesson_id,
            user_id=g.user.id,
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
        return render_template('class_detail/_grades.html', 
                             lesson_id=lesson_id,
                             user=g.user)
    except Exception as e:
        return f'<div class="alert alert-danger">Error loading grades: {str(e)}</div>', 500

