"""
Controller: Announcement
Handles HTTP requests for announcements
"""
from flask import jsonify, request, g, render_template
from datetime import datetime
from functools import wraps

from app.infrastructure.di.announcement_container import (
    get_announcement_service,
    get_comment_service
)


def get_announcement_controller():
    """Factory function for announcement controller"""
    return AnnouncementController(
        announcement_service=get_announcement_service(),
        comment_service=get_comment_service()
    )


class AnnouncementController:
    """Controller for announcement operations"""
    
    def __init__(self, announcement_service, comment_service):
        self.announcement_service = announcement_service
        self.comment_service = comment_service
    
    # ========================================
    # ANNOUNCEMENT CRUD
    # ========================================
    
    def list_announcements(self, lesson_id: str):
        """
        List all announcements for a lesson
        GET /class/<lesson_id>/stream
        """
        try:
            # Check if user has access to lesson (TODO: add permission check)
            include_drafts = False  # Only show drafts to teachers
            
            announcements = self.announcement_service.get_lesson_announcements(
                lesson_id=lesson_id,
                include_drafts=include_drafts
            )
            
            # Get comments for each announcement
            announcements_data = []
            for announcement in announcements:
                comments = self.comment_service.get_announcement_comments(
                    announcement_id=announcement.id,
                    include_private=False
                )
                
                announcement_dict = announcement.to_dict()
                announcement_dict['comments'] = [c.to_dict() for c in comments]
                announcements_data.append(announcement_dict)
            
            return render_template(
                'class_detail/_stream.html',
                lesson_id=lesson_id,
                announcements=announcements_data,
                user=g.user
            )
            
        except Exception as e:
            print(f"Error listing announcements: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    def create_announcement(self, lesson_id: str):
        """
        Create new announcement
        POST /class/<lesson_id>/announcements
        """
        try:
            data = request.get_json() if request.is_json else request.form
            
            title = data.get('title')
            content = data.get('content')
            is_pinned = data.get('is_pinned', False)
            allow_comments = data.get('allow_comments', True)
            scheduled_date = data.get('scheduled_date')
            is_published = data.get('is_published', True)
            
            if not title or not content:
                return jsonify({'error': 'Title and content are required'}), 400
            
            # Parse scheduled date if provided
            if scheduled_date:
                try:
                    scheduled_date = datetime.fromisoformat(scheduled_date)
                except:
                    scheduled_date = None
            
            announcement = self.announcement_service.create_announcement(
                lesson_id=lesson_id,
                title=title,
                content=content,
                created_by=g.user.id,
                is_pinned=bool(is_pinned),
                allow_comments=bool(allow_comments),
                scheduled_date=scheduled_date,
                is_published=bool(is_published)
            )
            
            return jsonify({
                'success': True,
                'message': 'Announcement created successfully',
                'announcement': announcement.to_dict()
            })
            
        except Exception as e:
            print(f"Error creating announcement: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    def get_announcement(self, lesson_id: str, announcement_id: str):
        """
        Get single announcement
        GET /class/<lesson_id>/announcements/<announcement_id>
        """
        try:
            announcement = self.announcement_service.get_announcement(announcement_id)
            
            if not announcement:
                return jsonify({'error': 'Announcement not found'}), 404
            
            if announcement.lesson_id != lesson_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            # Get comments
            comments = self.comment_service.get_announcement_comments(
                announcement_id=announcement_id,
                include_private=False
            )
            
            announcement_dict = announcement.to_dict()
            announcement_dict['comments'] = [c.to_dict() for c in comments]
            
            return jsonify({
                'success': True,
                'announcement': announcement_dict
            })
            
        except Exception as e:
            print(f"Error getting announcement: {e}")
            return jsonify({'error': str(e)}), 500
    
    def update_announcement(self, lesson_id: str, announcement_id: str):
        """
        Update announcement
        PUT /class/<lesson_id>/announcements/<announcement_id>
        """
        try:
            data = request.get_json() if request.is_json else request.form
            
            title = data.get('title')
            content = data.get('content')
            
            if not title or not content:
                return jsonify({'error': 'Title and content are required'}), 400
            
            announcement = self.announcement_service.update_announcement(
                announcement_id=announcement_id,
                title=title,
                content=content
            )
            
            return jsonify({
                'success': True,
                'message': 'Announcement updated successfully',
                'announcement': announcement.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            print(f"Error updating announcement: {e}")
            return jsonify({'error': str(e)}), 500
    
    def delete_announcement(self, lesson_id: str, announcement_id: str):
        """
        Delete announcement
        DELETE /class/<lesson_id>/announcements/<announcement_id>
        """
        try:
            success = self.announcement_service.delete_announcement(announcement_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Announcement deleted successfully'
                })
            else:
                return jsonify({'error': 'Announcement not found'}), 404
                
        except Exception as e:
            print(f"Error deleting announcement: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========================================
    # ANNOUNCEMENT ACTIONS
    # ========================================
    
    def pin_announcement(self, lesson_id: str, announcement_id: str):
        """
        Pin announcement
        POST /class/<lesson_id>/announcements/<announcement_id>/pin
        """
        try:
            announcement = self.announcement_service.pin_announcement(announcement_id)
            
            return jsonify({
                'success': True,
                'message': 'Announcement pinned',
                'announcement': announcement.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def unpin_announcement(self, lesson_id: str, announcement_id: str):
        """
        Unpin announcement
        POST /class/<lesson_id>/announcements/<announcement_id>/unpin
        """
        try:
            announcement = self.announcement_service.unpin_announcement(announcement_id)
            
            return jsonify({
                'success': True,
                'message': 'Announcement unpinned',
                'announcement': announcement.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def toggle_comments(self, lesson_id: str, announcement_id: str):
        """
        Toggle comments on/off
        POST /class/<lesson_id>/announcements/<announcement_id>/toggle-comments
        """
        try:
            announcement = self.announcement_service.toggle_comments(announcement_id)
            
            return jsonify({
                'success': True,
                'message': f"Comments {'enabled' if announcement.allow_comments else 'disabled'}",
                'announcement': announcement.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ========================================
    # COMMENTS
    # ========================================
    
    def create_comment(self, lesson_id: str, announcement_id: str):
        """
        Add comment to announcement
        POST /class/<lesson_id>/announcements/<announcement_id>/comments
        """
        try:
            data = request.get_json() if request.is_json else request.form
            
            content = data.get('content')
            parent_comment_id = data.get('parent_comment_id')
            
            if not content:
                return jsonify({'error': 'Content is required'}), 400
            
            comment = self.comment_service.create_comment(
                announcement_id=announcement_id,
                user_id=g.user.id,
                content=content,
                parent_comment_id=parent_comment_id,
                is_private=False
            )
            
            return jsonify({
                'success': True,
                'message': 'Comment added successfully',
                'comment': comment.to_dict()
            })
            
        except Exception as e:
            print(f"Error creating comment: {e}")
            return jsonify({'error': str(e)}), 500
    
    def update_comment(self, lesson_id: str, announcement_id: str, comment_id: str):
        """
        Update comment
        PUT /class/<lesson_id>/announcements/<announcement_id>/comments/<comment_id>
        """
        try:
            data = request.get_json() if request.is_json else request.form
            
            content = data.get('content')
            
            if not content:
                return jsonify({'error': 'Content is required'}), 400
            
            comment = self.comment_service.update_comment(comment_id, content)
            
            return jsonify({
                'success': True,
                'message': 'Comment updated successfully',
                'comment': comment.to_dict()
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def delete_comment(self, lesson_id: str, announcement_id: str, comment_id: str):
        """
        Delete comment
        DELETE /class/<lesson_id>/announcements/<announcement_id>/comments/<comment_id>
        """
        try:
            success = self.comment_service.delete_comment(comment_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Comment deleted successfully'
                })
            else:
                return jsonify({'error': 'Comment not found'}), 404
                
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return jsonify({'error': str(e)}), 500

