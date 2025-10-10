"""
Class/Lesson Routes
Routes for class/lesson management including pages, fragments, and CRUD operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify
from functools import wraps
from ..middleware.auth_middleware import login_required
from ..services import LessonService
from app import db
from sqlalchemy import text

# Create blueprint (no url_prefix to match existing routes)
class_bp = Blueprint('class', __name__)


@class_bp.before_request
def load_logged_in_user():
    """Load logged in user for class routes"""
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


def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# CLASS LIST & FRAGMENTS
# ============================================

@class_bp.route('/partial/class')
def partial_class_list():
    """Class/Lessons list fragment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lessons = lesson_service.get_lessons_by_user(g.user.id)
        
        # Sort: Favorites first, then by created_at
        lessons = sorted(lessons, key=lambda x: (x.is_favorite, x.created_at), reverse=True)
        
        # Check Microsoft Teams connection
        microsoft_teams_connected = session.get('microsoft_teams_connected', False)
        microsoft_teams_data = session.get('microsoft_teams_data', None)
        
        return render_template('class_fragment_new.html', 
                             lessons=lessons, 
                             user=g.user,
                             google_classroom_connected=False,
                             microsoft_teams_connected=microsoft_teams_connected,
                             microsoft_teams_data=microsoft_teams_data)
    except Exception as e:
        print(f"❌ Error loading lessons: {e}")
        import traceback
        traceback.print_exc()
        return render_template('class_fragment_new.html', 
                             lessons=[], 
                             user=g.user,
                             google_classroom_connected=False,
                             microsoft_teams_connected=False,
                             microsoft_teams_data=None)


# ============================================
# CLASS DETAIL & PAGES
# ============================================

@class_bp.route('/class/<lesson_id>')
def view_detail(lesson_id):
    """View class detail page with tabs"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        return render_template('class_detail.html', 
                             lesson=lesson, 
                             user=g.user)
    except Exception as e:
        print(f"Error loading class detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@class_bp.route('/class/<lesson_id>/classwork')
def get_classwork_data(lesson_id):
    """Get classwork data (tasks and materials) for a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson or lesson.user_id != g.user.id:
            return jsonify({'error': 'Class not found or no permission'}), 404
        
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
        print(f"Error loading classwork data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@class_bp.route('/partial/class/<lesson_id>/classwork')
def partial_classwork(lesson_id):
    """Classwork partial for specific class"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson or lesson.user_id != g.user.id:
            return '<div class="alert alert-danger">Class not found or no permission.</div>', 404
        
        return render_template('class_detail/_classwork.html', lesson=lesson)
    except Exception as e:
        print(f"Error loading classwork: {e}")
        return f'<div class="alert alert-danger">Error loading classwork: {str(e)}</div>', 500


# ============================================
# CRUD OPERATIONS
# ============================================

@class_bp.route('/partial/class/add', methods=['POST'])
def add_lesson():
    """Create new lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status', 'not_started')
        selected_color = request.form.get('selectedColor', '1')
        
        if not title:
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        
        # Convert color to integer
        try:
            color_theme = int(selected_color)
        except:
            color_theme = 1
        
        # Create lesson
        lesson = lesson_service.create_lesson(
            user_id=g.user.id,
            title=title,
            description=description or ''
        )
        
        # Update status and other fields
        status_map = {
            'not_started': 'not_started',
            'in_progress': 'in_progress', 
            'completed': 'completed',
            'archived': 'archived',
            'active': 'not_started'
        }
        status_value = status_map.get(status, 'not_started')
        
        # Get additional fields
        difficulty_level = request.form.get('difficulty_level', 'beginner')
        author_name = request.form.get('author_name', '')
        estimated_duration = request.form.get('estimated_duration', 0)
        tags = request.form.get('tags', '')
        
        # Convert duration to integer
        try:
            duration = int(estimated_duration) if estimated_duration else 0
        except:
            duration = 0
        
        db.session.execute(
            text("""
                UPDATE lesson 
                SET status = :status,
                    color_theme = :color_theme,
                    difficulty_level = :difficulty_level,
                    author_name = :author_name,
                    estimated_duration = :estimated_duration,
                    tags = :tags
                WHERE id = :lesson_id
            """),
            {
                "status": status_value,
                "color_theme": color_theme,
                "difficulty_level": difficulty_level,
                "author_name": author_name,
                "estimated_duration": duration,
                "tags": tags,
                "lesson_id": lesson.id
            }
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson created successfully',
            'lesson_id': lesson.id
        })
        
    except Exception as e:
        print(f"❌ Error creating lesson: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@class_bp.route('/partial/class/<lesson_id>/favorite', methods=['POST'])
def toggle_favorite(lesson_id):
    """Toggle lesson favorite status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'success': False, 'message': 'Lesson not found'}), 404
        
        # Toggle favorite
        new_favorite_status = not lesson.is_favorite
        
        db.session.execute(
            text("UPDATE lesson SET is_favorite = :fav WHERE id = :lesson_id AND user_id = :user_id"),
            {"fav": new_favorite_status, "lesson_id": lesson_id, "user_id": g.user.id}
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Favorite toggled successfully',
            'is_favorite': new_favorite_status
        })
    except Exception as e:
        print(f"❌ Error toggling favorite: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@class_bp.route('/partial/class/<lesson_id>/delete', methods=['POST'])
def delete_lesson(lesson_id):
    """Delete a lesson"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson_service.delete_lesson(lesson_id, g.user.id)
        
        return jsonify({
            'success': True,
            'message': 'Lesson deleted successfully'
        })
    except Exception as e:
        print(f"Error deleting lesson: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# DEBUG ROUTES
# ============================================

@class_bp.route('/debug/class/lessons')
def debug_lessons():
    """Debug route to check lessons data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lessons = lesson_service.get_lessons_by_user(g.user.id)
        
        lessons_data = []
        for lesson in lessons:
            lessons_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'status': str(lesson.status),
                'color_theme': lesson.color_theme,
                'created_at': str(lesson.created_at) if lesson.created_at else None,
                'is_favorite': lesson.is_favorite
            })
        
        return jsonify({
            'success': True,
            'user_id': g.user.id,
            'lessons_count': len(lessons),
            'lessons': lessons_data
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

