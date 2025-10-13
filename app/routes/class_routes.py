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
            return redirect(url_for('web_auth.login'))
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
        
        # Get classes where user is owner
        my_lessons = lesson_service.get_lessons_by_user(g.user.id)
        
        # Get classes where user is a member (shared with me)
        shared_lessons_data = db.session.execute(
            text("""
                SELECT l.id, l.user_id, l.title, l.description, l.content, 
                       l.status, l.color_theme, l.is_favorite, l.difficulty_level,
                       l.estimated_duration, l.author_name, l.tags, l.created_at, l.updated_at,
                       m.role as member_role
                FROM member m
                JOIN lesson l ON m.lesson_id = l.id
                WHERE m.user_id = :user_id
                ORDER BY m.joined_at DESC
            """),
            {'user_id': g.user.id}
        ).fetchall()
        
        # Convert shared lessons to lesson-like objects
        shared_lessons = []
        for row in shared_lessons_data:
            lesson_dict = {
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'description': row[3],
                'content': row[4],
                'status': row[5],
                'color_theme': row[6] or 1,
                'is_favorite': row[7] or False,
                'difficulty_level': row[8],
                'estimated_duration': row[9],
                'author_name': row[10],
                'tags': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'member_role': row[14],  # 'viewer'
                'is_shared': True
            }
            shared_lessons.append(type('Lesson', (), lesson_dict))
        
        # Sort my lessons: Favorites first, then by created_at
        my_lessons = sorted(my_lessons, key=lambda x: (not x.is_favorite, x.created_at), reverse=True)
        
        # Add is_shared flag to my lessons
        for lesson in my_lessons:
            lesson.is_shared = False
            lesson.member_role = 'owner'
        
        # Check Microsoft Teams connection
        microsoft_teams_connected = session.get('microsoft_teams_connected', False)
        microsoft_teams_data = session.get('microsoft_teams_data', None)
        
        return render_template('class_fragment.html', 
                             lessons=my_lessons,
                             shared_lessons=shared_lessons,
                             user=g.user,
                             google_classroom_connected=False,
                             microsoft_teams_connected=microsoft_teams_connected,
                             microsoft_teams_data=microsoft_teams_data)
    except Exception as e:
        print(f"❌ Error loading lessons: {e}")
        import traceback
        traceback.print_exc()
        return render_template('class_fragment.html', 
                             lessons=[], 
                             shared_lessons=[],
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
        return redirect(url_for('web_auth.login'))
    
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
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check permission: must be owner or member
        is_owner = lesson.user_id == g.user.id
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        if not is_owner and not member:
            return jsonify({'error': 'No permission'}), 403
        
        # Get classwork tasks (แต่ละคนมี tasks ของตัวเอง)
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
        
        # Get classwork materials (ทุกคนเห็น materials เดียวกัน - สร้างโดย owner)
        classwork_materials = db.session.execute(
            text("""
                SELECT id, title, description, file_path, file_type, file_size,
                       subject, category, tags, created_at, updated_at
                FROM classwork_material 
                WHERE lesson_id = :lesson_id AND user_id = :owner_id
                ORDER BY created_at DESC
            """),
            {'lesson_id': lesson_id, 'owner_id': lesson.user_id}
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
        
        if not lesson:
            return '<div class="alert alert-danger">Class not found.</div>', 404
        
        # Check permission: must be owner or member
        is_owner = lesson.user_id == g.user.id
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        if not is_owner and not member:
            return '<div class="alert alert-danger">You do not have permission to view this class.</div>', 403
        
        return render_template('class_detail/_classwork.html', lesson=lesson, is_owner=is_owner)
    except Exception as e:
        print(f"Error loading classwork: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading classwork: {str(e)}</div>', 500


@class_bp.route('/partial/class/<lesson_id>/people')
def partial_people(lesson_id):
    """People partial for specific class"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return '<div class="alert alert-danger">Class not found.</div>', 404
        
        # Check permission: must be owner or member
        is_owner = lesson.user_id == g.user.id
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        if not is_owner and not member:
            return '<div class="alert alert-danger">You do not have permission to view this class.</div>', 403
        
        return render_template('class_detail/_people.html', lesson=lesson, is_owner=is_owner)
    except Exception as e:
        print(f"Error loading people: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading people: {str(e)}</div>', 500


@class_bp.route('/partial/class/<lesson_id>/stream')
def partial_stream(lesson_id):
    """Stream partial for specific class (Q&A + Announcements)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return '<div class="alert alert-danger">Class not found.</div>', 404
        
        # Check permission: must be owner or member
        is_owner = lesson.user_id == g.user.id
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        if not is_owner and not member:
            return '<div class="alert alert-danger">You do not have permission to view this class.</div>', 403
        
        # Pass user info to template (as dict to avoid serialization issues)
        user_name = g.user.username
        if g.user.first_name and g.user.last_name:
            user_name = f"{g.user.first_name} {g.user.last_name}"
        elif g.user.first_name:
            user_name = g.user.first_name
        
        user_data = {
            'id': g.user.id,
            'name': user_name,
            'email': g.user.email,
            'username': g.user.username
        }
        
        return render_template('class_detail/_stream.html', 
                             lesson=lesson, 
                             is_owner=is_owner,
                             current_user=user_data)
    except Exception as e:
        print(f"Error loading stream: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading stream: {str(e)}</div>', 500


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
# PEOPLE / MEMBERS API
# ============================================

@class_bp.route('/api/class/<lesson_id>/members', methods=['GET'])
def get_members(lesson_id):
    """Get all members of a class"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check permission
        is_owner = lesson.user_id == g.user.id
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        if not is_owner and not member:
            return jsonify({'error': 'No permission'}), 403
        
        # Get owner info
        owner_data = db.session.execute(
            text("SELECT id, username, email, profile_image FROM user WHERE id = :user_id"),
            {'user_id': lesson.user_id}
        ).fetchone()
        
        owner = {
            'id': owner_data[0],
            'user_id': owner_data[0],
            'username': owner_data[1],
            'email': owner_data[2],
            'profile_image': owner_data[3],
            'role': 'owner'
        } if owner_data else None
        
        # Get members
        members_data = db.session.execute(
            text("""
                SELECT m.id, m.user_id, m.role, m.joined_at,
                       u.username, u.email, u.profile_image
                FROM member m
                JOIN user u ON m.user_id = u.id
                WHERE m.lesson_id = :lesson_id
                ORDER BY m.joined_at DESC
            """),
            {'lesson_id': lesson_id}
        ).fetchall()
        
        members = [{
            'id': row[0],
            'user_id': row[1],
            'role': row[2],
            'joined_at': row[3],
            'username': row[4],
            'email': row[5],
            'profile_image': row[6]
        } for row in members_data]
        
        return jsonify({
            'success': True,
            'data': {
                'owner': owner,
                'members': members,
                'total': len(members) + (1 if owner else 0)
            }
        })
    except Exception as e:
        print(f"Error getting members: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@class_bp.route('/api/users/search', methods=['GET'])
def search_users():
    """Search users by username"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        query = request.args.get('username', '').strip()
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'data': {'users': []}
            })
        
        # Search users (exclude current user)
        users_data = db.session.execute(
            text("""
                SELECT id, username, email, profile_image
                FROM user
                WHERE (username LIKE :query OR email LIKE :query)
                AND id != :current_user_id
                AND is_active = 1
                LIMIT 10
            """),
            {'query': f'%{query}%', 'current_user_id': g.user.id}
        ).fetchall()
        
        users = [{
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'profile_image': row[3]
        } for row in users_data]
        
        return jsonify({
            'success': True,
            'data': {'users': users}
        })
    except Exception as e:
        print(f"Error searching users: {e}")
        return jsonify({'error': str(e)}), 500


@class_bp.route('/api/class/<lesson_id>/members', methods=['POST'])
def add_member(lesson_id):
    """Add a member to a class"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check permission: only owner can add members
        if lesson.user_id != g.user.id:
            return jsonify({'error': 'Only owner can add members'}), 403
        
        data = request.get_json()
        new_user_id = data.get('user_id')
        
        if not new_user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Check if user exists
        user_exists = db.session.execute(
            text("SELECT id FROM user WHERE id = :user_id"),
            {'user_id': new_user_id}
        ).fetchone()
        
        if not user_exists:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already a member
        existing = db.session.execute(
            text("SELECT id FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': new_user_id}
        ).fetchone()
        
        if existing:
            return jsonify({'error': 'User is already a member'}), 409
        
        # Add member
        import uuid
        from datetime import datetime
        
        member_id = str(uuid.uuid4())
        db.session.execute(
            text("""
                INSERT INTO member (id, lesson_id, user_id, role, invited_by, joined_at)
                VALUES (:id, :lesson_id, :user_id, :role, :invited_by, :joined_at)
            """),
            {
                'id': member_id,
                'lesson_id': lesson_id,
                'user_id': new_user_id,
                'role': 'viewer',
                'invited_by': g.user.id,
                'joined_at': datetime.utcnow()
            }
        )
        db.session.commit()
        
        # Auto-generate activity
        try:
            from ..controllers.stream_views import StreamController
            stream_controller = StreamController()
            
            # Get new member info
            new_member = db.session.execute(
                text("SELECT name FROM user WHERE id = :user_id"),
                {'user_id': new_user_id}
            ).fetchone()
            
            if new_member:
                stream_controller.create_activity(
                    lesson_id=lesson_id,
                    user_id=new_user_id,
                    activity_type='member_joined',
                    title=f'{new_member.name} joined the class'
                )
        except Exception as e:
            print(f"Warning: Failed to create activity: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Member added successfully',
            'data': {'member_id': member_id}
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding member: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@class_bp.route('/api/class/<lesson_id>/members/<user_id>', methods=['DELETE'])
def remove_member(lesson_id, user_id):
    """Remove a member from a class"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check permission: only owner can remove members
        if lesson.user_id != g.user.id:
            return jsonify({'error': 'Only owner can remove members'}), 403
        
        # Cannot remove owner
        if user_id == lesson.user_id:
            return jsonify({'error': 'Cannot remove owner'}), 400
        
        # Remove member
        result = db.session.execute(
            text("DELETE FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': user_id}
        )
        db.session.commit()
        
        if result.rowcount == 0:
            return jsonify({'error': 'Member not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Member removed successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error removing member: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================
# SETTINGS ROUTES
# ============================================

@class_bp.route('/partial/class/<lesson_id>/settings')
@login_required_web
def partial_settings(lesson_id):
    """Settings fragment for a specific class"""
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Check permission
        is_owner = lesson.user_id == g.user.id
        if not is_owner:
            # Check if user is a member
            member = db.session.execute(
                text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
                {'lesson_id': lesson_id, 'user_id': g.user.id}
            ).fetchone()
            
            if not member:
                return jsonify({'error': 'Access denied'}), 403
        
        return render_template('class_detail/_settings.html', 
                             lesson=lesson, 
                             is_owner=is_owner)
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@class_bp.route('/api/class/<lesson_id>/settings', methods=['PUT'])
@login_required_web
def update_class_settings(lesson_id):
    """Update class settings"""
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Only owner can update settings
        if lesson.user_id != g.user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update lesson fields
        if 'title' in data:
            lesson.title = data['title'].strip()
        if 'description' in data:
            lesson.description = data['description'].strip()
        if 'visibility' in data:
            # Store visibility in lesson metadata or separate table
            # For now, we'll skip this as it requires schema changes
            pass
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@class_bp.route('/api/class/<lesson_id>', methods=['DELETE'])
@login_required_web
def delete_class(lesson_id):
    """Delete a class (owner only)"""
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Only owner can delete class
        if lesson.user_id != g.user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete all related data
        # 1. Delete members
        db.session.execute(
            text("DELETE FROM member WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        
        # 2. Delete classwork tasks
        db.session.execute(
            text("DELETE FROM classwork_task WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        
        # 3. Delete classwork materials
        db.session.execute(
            text("DELETE FROM classwork_material WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        
        # 4. Delete grades (cascade should handle this, but let's be explicit)
        db.session.execute(
            text("DELETE FROM grade_entry WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        db.session.execute(
            text("DELETE FROM grade_item WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        db.session.execute(
            text("DELETE FROM grade_category WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        db.session.execute(
            text("DELETE FROM grade_config WHERE lesson_id = :lesson_id"),
            {'lesson_id': lesson_id}
        )
        
        # 5. Delete lesson itself
        db.session.delete(lesson)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Class deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@class_bp.route('/api/class/<lesson_id>/leave', methods=['POST'])
@login_required_web
def leave_class(lesson_id):
    """Leave a class (viewers only)"""
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Class not found'}), 404
        
        # Owner cannot leave their own class
        if lesson.user_id == g.user.id:
            return jsonify({'error': 'Owner cannot leave their own class'}), 400
        
        # Check if user is a member
        member = db.session.execute(
            text("SELECT * FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        ).fetchone()
        
        if not member:
            return jsonify({'error': 'You are not a member of this class'}), 400
        
        # Auto-generate activity before removing
        try:
            from ..controllers.stream_views import StreamController
            stream_controller = StreamController()
            stream_controller.create_activity(
                lesson_id=lesson_id,
                user_id=g.user.id,
                activity_type='member_left',
                title=f'{g.user.name} left the class'
            )
        except Exception as e:
            print(f"Warning: Failed to create activity: {e}")
        
        # Remove member
        db.session.execute(
            text("DELETE FROM member WHERE lesson_id = :lesson_id AND user_id = :user_id"),
            {'lesson_id': lesson_id, 'user_id': g.user.id}
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully left the class'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


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

