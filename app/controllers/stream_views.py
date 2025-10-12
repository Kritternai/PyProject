"""
Stream System Controllers
Business logic for Q&A + Announcements + Activity Timeline
"""

from app import db
from app.models.stream import StreamPost, StreamComment, StreamAttachment
from sqlalchemy import text
from datetime import datetime
import uuid


class StreamController:
    """Controller for Stream System"""
    
    # ============================================
    # Posts Management
    # ============================================
    
    def get_posts(self, lesson_id, post_type=None, user_id=None):
        """
        Get all posts for a lesson
        
        Args:
            lesson_id: Lesson ID
            post_type: Filter by type ('question', 'announcement', 'activity')
            user_id: Filter by user (for author filter)
        
        Returns:
            List of posts with author and stats
        """
        try:
            query = """
                SELECT 
                    sp.*,
                    u.name as author_name,
                    u.email as author_email,
                    (SELECT COUNT(*) FROM stream_comment WHERE post_id = sp.id) as comments_count,
                    (SELECT COUNT(*) FROM stream_attachment WHERE post_id = sp.id) as attachments_count
                FROM stream_post sp
                LEFT JOIN user u ON sp.user_id = u.id
                WHERE sp.lesson_id = :lesson_id
            """
            
            params = {'lesson_id': lesson_id}
            
            if post_type:
                query += " AND sp.type = :post_type"
                params['post_type'] = post_type
            
            if user_id:
                query += " AND sp.user_id = :user_id"
                params['user_id'] = user_id
            
            query += " ORDER BY sp.is_pinned DESC, sp.created_at DESC"
            
            result = db.session.execute(text(query), params)
            posts = []
            
            for row in result:
                post = {
                    'id': row.id,
                    'lesson_id': row.lesson_id,
                    'user_id': row.user_id,
                    'type': row.type,
                    'title': row.title,
                    'content': row.content,
                    'is_pinned': bool(row.is_pinned),
                    'allow_comments': bool(row.allow_comments),
                    'has_accepted_answer': bool(row.has_accepted_answer),
                    'accepted_answer_id': row.accepted_answer_id,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at,
                    'author': {
                        'id': row.user_id,
                        'name': row.author_name,
                        'email': row.author_email
                    },
                    'comments_count': row.comments_count or 0,
                    'attachments_count': row.attachments_count or 0
                }
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    def get_post_by_id(self, post_id):
        """Get single post with details"""
        try:
            query = """
                SELECT 
                    sp.*,
                    u.name as author_name,
                    u.email as author_email
                FROM stream_post sp
                LEFT JOIN user u ON sp.user_id = u.id
                WHERE sp.id = :post_id
            """
            
            result = db.session.execute(text(query), {'post_id': post_id}).fetchone()
            
            if not result:
                return None
            
            post = {
                'id': result.id,
                'lesson_id': result.lesson_id,
                'user_id': result.user_id,
                'type': result.type,
                'title': result.title,
                'content': result.content,
                'is_pinned': bool(result.is_pinned),
                'allow_comments': bool(result.allow_comments),
                'has_accepted_answer': bool(result.has_accepted_answer),
                'accepted_answer_id': result.accepted_answer_id,
                'created_at': result.created_at,
                'updated_at': result.updated_at,
                'author': {
                    'id': result.user_id,
                    'name': result.author_name,
                    'email': result.author_email
                }
            }
            
            # Get comments
            post['comments'] = self.get_comments(post_id)
            
            # Get attachments
            post['attachments'] = self.get_attachments(post_id)
            
            return post
            
        except Exception as e:
            print(f"Error getting post: {e}")
            return None
    
    def create_post(self, lesson_id, user_id, data):
        """
        Create new post
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID (author)
            data: Post data (type, title, content, etc.)
        
        Returns:
            Created post or None
        """
        try:
            post_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO stream_post (
                    id, lesson_id, user_id, type, title, content,
                    is_pinned, allow_comments, created_at
                ) VALUES (
                    :id, :lesson_id, :user_id, :type, :title, :content,
                    :is_pinned, :allow_comments, :created_at
                )
            """
            
            params = {
                'id': post_id,
                'lesson_id': lesson_id,
                'user_id': user_id,
                'type': data.get('type', 'question'),
                'title': data.get('title'),
                'content': data.get('content'),
                'is_pinned': data.get('is_pinned', False),
                'allow_comments': data.get('allow_comments', True),
                'created_at': datetime.utcnow()
            }
            
            db.session.execute(text(query), params)
            db.session.commit()
            
            return self.get_post_by_id(post_id)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating post: {e}")
            return None
    
    def update_post(self, post_id, data):
        """Update post"""
        try:
            updates = []
            params = {'id': post_id, 'updated_at': datetime.utcnow()}
            
            if 'title' in data:
                updates.append("title = :title")
                params['title'] = data['title']
            
            if 'content' in data:
                updates.append("content = :content")
                params['content'] = data['content']
            
            if 'type' in data:
                updates.append("type = :type")
                params['type'] = data['type']
            
            if 'allow_comments' in data:
                updates.append("allow_comments = :allow_comments")
                params['allow_comments'] = data['allow_comments']
            
            if not updates:
                return self.get_post_by_id(post_id)
            
            query = f"""
                UPDATE stream_post 
                SET {', '.join(updates)}, updated_at = :updated_at
                WHERE id = :id
            """
            
            db.session.execute(text(query), params)
            db.session.commit()
            
            return self.get_post_by_id(post_id)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating post: {e}")
            return None
    
    def delete_post(self, post_id):
        """Delete post (cascade delete comments and attachments)"""
        try:
            query = "DELETE FROM stream_post WHERE id = :id"
            db.session.execute(text(query), {'id': post_id})
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting post: {e}")
            return False
    
    def toggle_pin(self, post_id):
        """Toggle pin status"""
        try:
            query = """
                UPDATE stream_post 
                SET is_pinned = NOT is_pinned, updated_at = :updated_at
                WHERE id = :id
            """
            
            db.session.execute(text(query), {
                'id': post_id,
                'updated_at': datetime.utcnow()
            })
            db.session.commit()
            
            return self.get_post_by_id(post_id)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error toggling pin: {e}")
            return None
    
    def toggle_comments(self, post_id):
        """Toggle allow_comments"""
        try:
            query = """
                UPDATE stream_post 
                SET allow_comments = NOT allow_comments, updated_at = :updated_at
                WHERE id = :id
            """
            
            db.session.execute(text(query), {
                'id': post_id,
                'updated_at': datetime.utcnow()
            })
            db.session.commit()
            
            return self.get_post_by_id(post_id)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error toggling comments: {e}")
            return None
    
    # ============================================
    # Comments Management
    # ============================================
    
    def get_comments(self, post_id):
        """Get all comments for a post"""
        try:
            query = """
                SELECT 
                    sc.*,
                    u.name as author_name,
                    u.email as author_email
                FROM stream_comment sc
                LEFT JOIN user u ON sc.user_id = u.id
                WHERE sc.post_id = :post_id
                ORDER BY sc.is_accepted DESC, sc.created_at ASC
            """
            
            result = db.session.execute(text(query), {'post_id': post_id})
            comments = []
            
            for row in result:
                comment = {
                    'id': row.id,
                    'post_id': row.post_id,
                    'user_id': row.user_id,
                    'content': row.content,
                    'is_accepted': bool(row.is_accepted),
                    'created_at': row.created_at,
                    'updated_at': row.updated_at,
                    'author': {
                        'id': row.user_id,
                        'name': row.author_name,
                        'email': row.author_email
                    }
                }
                comments.append(comment)
            
            return comments
            
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []
    
    def add_comment(self, post_id, user_id, content):
        """Add comment to post"""
        try:
            query = """
                INSERT INTO stream_comment (post_id, user_id, content, created_at)
                VALUES (:post_id, :user_id, :content, :created_at)
            """
            
            db.session.execute(text(query), {
                'post_id': post_id,
                'user_id': user_id,
                'content': content,
                'created_at': datetime.utcnow()
            })
            db.session.commit()
            
            return self.get_comments(post_id)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding comment: {e}")
            return None
    
    def update_comment(self, comment_id, content):
        """Update comment"""
        try:
            query = """
                UPDATE stream_comment 
                SET content = :content, updated_at = :updated_at
                WHERE id = :id
            """
            
            db.session.execute(text(query), {
                'id': comment_id,
                'content': content,
                'updated_at': datetime.utcnow()
            })
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating comment: {e}")
            return False
    
    def delete_comment(self, comment_id):
        """Delete comment"""
        try:
            query = "DELETE FROM stream_comment WHERE id = :id"
            db.session.execute(text(query), {'id': comment_id})
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting comment: {e}")
            return False
    
    def accept_answer(self, post_id, comment_id):
        """Mark comment as accepted answer (Q&A)"""
        try:
            # Unaccept all other answers first
            query1 = """
                UPDATE stream_comment 
                SET is_accepted = 0
                WHERE post_id = :post_id
            """
            db.session.execute(text(query1), {'post_id': post_id})
            
            # Accept this answer
            query2 = """
                UPDATE stream_comment 
                SET is_accepted = 1
                WHERE id = :id
            """
            db.session.execute(text(query2), {'id': comment_id})
            
            # Update post
            query3 = """
                UPDATE stream_post 
                SET has_accepted_answer = 1, accepted_answer_id = :comment_id
                WHERE id = :post_id
            """
            db.session.execute(text(query3), {
                'post_id': post_id,
                'comment_id': comment_id
            })
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error accepting answer: {e}")
            return False
    
    # ============================================
    # Attachments Management
    # ============================================
    
    def get_attachments(self, post_id):
        """Get all attachments for a post"""
        try:
            query = """
                SELECT * FROM stream_attachment
                WHERE post_id = :post_id
                ORDER BY created_at ASC
            """
            
            result = db.session.execute(text(query), {'post_id': post_id})
            attachments = []
            
            for row in result:
                attachment = {
                    'id': row.id,
                    'post_id': row.post_id,
                    'type': row.type,
                    'name': row.name,
                    'url': row.url,
                    'size': row.size,
                    'mime_type': row.mime_type,
                    'created_at': row.created_at
                }
                attachments.append(attachment)
            
            return attachments
            
        except Exception as e:
            print(f"Error getting attachments: {e}")
            return []
    
    def add_attachment(self, post_id, data):
        """Add attachment to post"""
        try:
            query = """
                INSERT INTO stream_attachment (
                    post_id, type, name, url, size, mime_type, created_at
                ) VALUES (
                    :post_id, :type, :name, :url, :size, :mime_type, :created_at
                )
            """
            
            db.session.execute(text(query), {
                'post_id': post_id,
                'type': data.get('type', 'file'),
                'name': data.get('name'),
                'url': data.get('url'),
                'size': data.get('size'),
                'mime_type': data.get('mime_type'),
                'created_at': datetime.utcnow()
            })
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding attachment: {e}")
            return False
    
    def delete_attachment(self, attachment_id):
        """Delete attachment"""
        try:
            query = "DELETE FROM stream_attachment WHERE id = :id"
            db.session.execute(text(query), {'id': attachment_id})
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting attachment: {e}")
            return False
    
    # ============================================
    # Activity Generation
    # ============================================
    
    def create_activity(self, lesson_id, user_id, activity_type, title, content=None):
        """
        Create activity post (auto-generated)
        
        Activity types:
        - member_joined
        - member_left
        - task_created
        - material_uploaded
        - grade_added
        """
        try:
            post_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO stream_post (
                    id, lesson_id, user_id, type, title, content,
                    allow_comments, created_at
                ) VALUES (
                    :id, :lesson_id, :user_id, 'activity', :title, :content,
                    0, :created_at
                )
            """
            
            db.session.execute(text(query), {
                'id': post_id,
                'lesson_id': lesson_id,
                'user_id': user_id,
                'title': activity_type,
                'content': content or title,
                'created_at': datetime.utcnow()
            })
            db.session.commit()
            
            return post_id
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating activity: {e}")
            return None
    
    # ============================================
    # Statistics
    # ============================================
    
    def get_stats(self, lesson_id):
        """Get stream statistics"""
        try:
            query = """
                SELECT 
                    COUNT(CASE WHEN type = 'question' THEN 1 END) as questions_count,
                    COUNT(CASE WHEN type = 'announcement' THEN 1 END) as announcements_count,
                    COUNT(CASE WHEN type = 'activity' THEN 1 END) as activities_count,
                    COUNT(*) as total_posts,
                    (SELECT COUNT(*) FROM stream_comment sc 
                     JOIN stream_post sp ON sc.post_id = sp.id 
                     WHERE sp.lesson_id = :lesson_id) as total_comments
                FROM stream_post
                WHERE lesson_id = :lesson_id
            """
            
            result = db.session.execute(text(query), {'lesson_id': lesson_id}).fetchone()
            
            return {
                'questions_count': result.questions_count or 0,
                'announcements_count': result.announcements_count or 0,
                'activities_count': result.activities_count or 0,
                'total_posts': result.total_posts or 0,
                'total_comments': result.total_comments or 0
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'questions_count': 0,
                'announcements_count': 0,
                'activities_count': 0,
                'total_posts': 0,
                'total_comments': 0
            }

