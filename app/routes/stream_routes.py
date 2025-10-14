"""
Stream System Routes
API endpoints for Q&A + Announcements + Activity Timeline
"""

from flask import Blueprint, jsonify, request, session, g
from functools import wraps
from ..controllers.stream_views import StreamController
from ..services import LessonService
from app import db
from sqlalchemy import text

# Create blueprint
stream_bp = Blueprint('stream', __name__)

# Initialize controller
stream_controller = StreamController()


def login_required_api(f):
    """Decorator to require login for API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


def check_class_permission(lesson_id, user_id, require_owner=False):
    """Check if user has permission to access class"""
    try:
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
        
    except Exception as e:
        # Log the actual error details for debugging
        import traceback
        print(f"Error checking permission: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return False, False


# ============================================
# Posts Routes
# ============================================

@stream_bp.route('/api/class/<lesson_id>/stream/posts', methods=['GET'])
@login_required_api
def get_posts(lesson_id):
    """Get all posts for a class"""
    try:
        user_id = session.get('user_id')
        has_permission, is_owner = check_class_permission(lesson_id, user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Get filters from query params
        post_type = request.args.get('type')  # question, announcement, activity
        author_filter = request.args.get('author')  # owner, member
        
        filter_user_id = None
        if author_filter == 'owner':
            # Get owner's user_id
            lesson_service = LessonService()
            lesson = lesson_service.get_lesson_by_id(lesson_id)
            filter_user_id = lesson.user_id if lesson else None
        elif author_filter == 'member':
            filter_user_id = user_id
        
        posts = stream_controller.get_posts(lesson_id, post_type, filter_user_id)
        
        return jsonify({
            'success': True,
            'posts': posts,
            'is_owner': is_owner
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/class/<lesson_id>/stream/posts', methods=['POST'])
@login_required_api
def create_post(lesson_id):
    """Create new post"""
    try:
        user_id = session.get('user_id')
        has_permission, is_owner = check_class_permission(lesson_id, user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        data = request.get_json()
        post_type = data.get('type', 'question')
        
        # Only owner can create announcements
        if post_type == 'announcement' and not is_owner:
            return jsonify({'success': False, 'error': 'Only owner can create announcements'}), 403
        
        # Validate required fields
        if not data.get('content'):
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        post = stream_controller.create_post(lesson_id, user_id, data)
        
        if post:
            return jsonify({
                'success': True,
                'message': 'Post created successfully',
                'post': post
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create post'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>', methods=['GET'])
@login_required_api
def get_post(post_id):
    """Get single post with details"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Check permission
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        return jsonify({
            'success': True,
            'post': post,
            'is_owner': is_owner
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>', methods=['PUT'])
@login_required_api
def update_post(post_id):
    """Update post"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Check if user is author or owner
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Only author or owner can edit
        if post['user_id'] != user_id and not is_owner:
            return jsonify({'success': False, 'error': 'Only author or owner can edit'}), 403
        
        data = request.get_json()
        updated_post = stream_controller.update_post(post_id, data)
        
        if updated_post:
            return jsonify({
                'success': True,
                'message': 'Post updated successfully',
                'post': updated_post
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update post'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>', methods=['DELETE'])
@login_required_api
def delete_post(post_id):
    """Delete post"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Check if user is author or owner
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Only author or owner can delete
        if post['user_id'] != user_id and not is_owner:
            return jsonify({'success': False, 'error': 'Only author or owner can delete'}), 403
        
        success = stream_controller.delete_post(post_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Post deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete post'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>/pin', methods=['POST'])
@login_required_api
def toggle_pin(post_id):
    """Toggle pin status (owner only)"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Only owner can pin
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id, require_owner=True)
        
        if not is_owner:
            return jsonify({'success': False, 'error': 'Only owner can pin posts'}), 403
        
        updated_post = stream_controller.toggle_pin(post_id)
        
        if updated_post:
            return jsonify({
                'success': True,
                'message': 'Pin status updated',
                'post': updated_post
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update pin status'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>/toggle-comments', methods=['POST'])
@login_required_api
def toggle_comments(post_id):
    """Toggle allow_comments (owner only)"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Only owner can toggle comments
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id, require_owner=True)
        
        if not is_owner:
            return jsonify({'success': False, 'error': 'Only owner can toggle comments'}), 403
        
        updated_post = stream_controller.toggle_comments(post_id)
        
        if updated_post:
            return jsonify({
                'success': True,
                'message': 'Comments setting updated',
                'post': updated_post
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update comments setting'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Comments Routes
# ============================================

@stream_bp.route('/api/stream/posts/<post_id>/comments', methods=['GET'])
@login_required_api
def get_comments(post_id):
    """Get all comments for a post"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Check permission
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        comments = stream_controller.get_comments(post_id)
        
        return jsonify({
            'success': True,
            'comments': comments
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>/comments', methods=['POST'])
@login_required_api
def add_comment(post_id):
    """Add comment to post"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Check permission
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Check if comments are allowed
        if not post['allow_comments']:
            return jsonify({'success': False, 'error': 'Comments are disabled for this post'}), 403
        
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        comments = stream_controller.add_comment(post_id, user_id, content)
        
        if comments is not None:
            return jsonify({
                'success': True,
                'message': 'Comment added successfully',
                'comments': comments
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add comment'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/comments/<int:comment_id>', methods=['PUT'])
@login_required_api
def update_comment(comment_id):
    """Update comment"""
    try:
        user_id = session.get('user_id')
        
        # Get comment to check ownership
        query = "SELECT * FROM stream_comment WHERE id = :id"
        comment = db.session.execute(text(query), {'id': comment_id}).fetchone()
        
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found'}), 404
        
        # Only author can edit their comment
        if comment.user_id != user_id:
            return jsonify({'success': False, 'error': 'Only author can edit comment'}), 403
        
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        success = stream_controller.update_comment(comment_id, content)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Comment updated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update comment'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/comments/<int:comment_id>', methods=['DELETE'])
@login_required_api
def delete_comment(comment_id):
    """Delete comment"""
    try:
        user_id = session.get('user_id')
        
        # Get comment to check ownership
        query = """
            SELECT sc.*, sp.lesson_id, sp.user_id as post_author_id
            FROM stream_comment sc
            JOIN stream_post sp ON sc.post_id = sp.id
            WHERE sc.id = :id
        """
        comment = db.session.execute(text(query), {'id': comment_id}).fetchone()
        
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found'}), 404
        
        # Check if user is comment author or class owner
        has_permission, is_owner = check_class_permission(comment.lesson_id, user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Author or owner can delete
        if comment.user_id != user_id and not is_owner:
            return jsonify({'success': False, 'error': 'Only author or owner can delete comment'}), 403
        
        success = stream_controller.delete_comment(comment_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Comment deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete comment'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stream_bp.route('/api/stream/posts/<post_id>/accept-answer/<int:comment_id>', methods=['POST'])
@login_required_api
def accept_answer(post_id, comment_id):
    """Mark comment as accepted answer (owner only)"""
    try:
        user_id = session.get('user_id')
        post = stream_controller.get_post_by_id(post_id)
        
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Only owner can accept answers
        has_permission, is_owner = check_class_permission(post['lesson_id'], user_id, require_owner=True)
        
        if not is_owner:
            return jsonify({'success': False, 'error': 'Only owner can accept answers'}), 403
        
        success = stream_controller.accept_answer(post_id, comment_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Answer accepted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to accept answer'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Statistics Route
# ============================================

@stream_bp.route('/api/class/<lesson_id>/stream/stats', methods=['GET'])
@login_required_api
def get_stats(lesson_id):
    """Get stream statistics"""
    try:
        user_id = session.get('user_id')
        has_permission, is_owner = check_class_permission(lesson_id, user_id)
        
        if not has_permission:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        stats = stream_controller.get_stats(lesson_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

