"""
Repository Implementation: Announcement (SQLAlchemy)
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text

from app import db
from app.domain.entities.announcement import Announcement, AnnouncementComment
from app.domain.interfaces.announcement_repository import (
    AnnouncementRepository,
    AnnouncementCommentRepository
)


class SQLAlchemyAnnouncementRepository(AnnouncementRepository):
    """SQLAlchemy implementation of AnnouncementRepository"""
    
    def create(self, announcement: Announcement) -> Announcement:
        """Create new announcement"""
        if not announcement.id:
            announcement.id = str(uuid.uuid4())
        
        if not announcement.created_at:
            announcement.created_at = datetime.utcnow()
        
        if not announcement.updated_at:
            announcement.updated_at = datetime.utcnow()
        
        query = text("""
            INSERT INTO lesson_announcement (
                id, lesson_id, title, content,
                is_pinned, allow_comments, scheduled_date, is_published,
                created_by, created_at, updated_at
            ) VALUES (
                :id, :lesson_id, :title, :content,
                :is_pinned, :allow_comments, :scheduled_date, :is_published,
                :created_by, :created_at, :updated_at
            )
        """)
        
        db.session.execute(query, {
            'id': announcement.id,
            'lesson_id': announcement.lesson_id,
            'title': announcement.title,
            'content': announcement.content,
            'is_pinned': announcement.is_pinned,
            'allow_comments': announcement.allow_comments,
            'scheduled_date': announcement.scheduled_date,
            'is_published': announcement.is_published,
            'created_by': announcement.created_by,
            'created_at': announcement.created_at,
            'updated_at': announcement.updated_at
        })
        db.session.commit()
        
        return announcement
    
    def get_by_id(self, announcement_id: str) -> Optional[Announcement]:
        """Get announcement by ID"""
        query = text("""
            SELECT * FROM lesson_announcement WHERE id = :id
        """)
        
        result = db.session.execute(query, {'id': announcement_id}).fetchone()
        
        if not result:
            return None
        
        return self._row_to_entity(result)
    
    def get_by_lesson(self, lesson_id: str, include_drafts: bool = False) -> List[Announcement]:
        """Get all announcements for a lesson"""
        if include_drafts:
            query = text("""
                SELECT a.*, COUNT(DISTINCT c.id) as comment_count
                FROM lesson_announcement a
                LEFT JOIN announcement_comment c ON a.id = c.announcement_id
                WHERE a.lesson_id = :lesson_id
                GROUP BY a.id
                ORDER BY a.is_pinned DESC, a.created_at DESC
            """)
        else:
            query = text("""
                SELECT a.*, COUNT(DISTINCT c.id) as comment_count
                FROM lesson_announcement a
                LEFT JOIN announcement_comment c ON a.id = c.announcement_id
                WHERE a.lesson_id = :lesson_id AND a.is_published = 1
                AND (a.scheduled_date IS NULL OR a.scheduled_date <= :now)
                GROUP BY a.id
                ORDER BY a.is_pinned DESC, a.created_at DESC
            """)
        
        params = {'lesson_id': lesson_id}
        if not include_drafts:
            params['now'] = datetime.utcnow()
        
        results = db.session.execute(query, params).fetchall()
        
        return [self._row_to_entity(row) for row in results]
    
    def get_pinned(self, lesson_id: str) -> List[Announcement]:
        """Get pinned announcements"""
        query = text("""
            SELECT a.*, COUNT(DISTINCT c.id) as comment_count
            FROM lesson_announcement a
            LEFT JOIN announcement_comment c ON a.id = c.announcement_id
            WHERE a.lesson_id = :lesson_id AND a.is_pinned = 1 AND a.is_published = 1
            GROUP BY a.id
            ORDER BY a.created_at DESC
        """)
        
        results = db.session.execute(query, {'lesson_id': lesson_id}).fetchall()
        
        return [self._row_to_entity(row) for row in results]
    
    def get_scheduled(self, lesson_id: str) -> List[Announcement]:
        """Get scheduled announcements"""
        query = text("""
            SELECT * FROM lesson_announcement
            WHERE lesson_id = :lesson_id 
            AND scheduled_date IS NOT NULL 
            AND scheduled_date > :now
            ORDER BY scheduled_date ASC
        """)
        
        results = db.session.execute(query, {
            'lesson_id': lesson_id,
            'now': datetime.utcnow()
        }).fetchall()
        
        return [self._row_to_entity(row) for row in results]
    
    def update(self, announcement: Announcement) -> Announcement:
        """Update announcement"""
        announcement.updated_at = datetime.utcnow()
        
        query = text("""
            UPDATE lesson_announcement
            SET title = :title, content = :content,
                is_pinned = :is_pinned, allow_comments = :allow_comments,
                scheduled_date = :scheduled_date, is_published = :is_published,
                updated_at = :updated_at
            WHERE id = :id
        """)
        
        db.session.execute(query, {
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_pinned': announcement.is_pinned,
            'allow_comments': announcement.allow_comments,
            'scheduled_date': announcement.scheduled_date,
            'is_published': announcement.is_published,
            'updated_at': announcement.updated_at
        })
        db.session.commit()
        
        return announcement
    
    def delete(self, announcement_id: str) -> bool:
        """Delete announcement"""
        query = text("""
            DELETE FROM lesson_announcement WHERE id = :id
        """)
        
        result = db.session.execute(query, {'id': announcement_id})
        db.session.commit()
        
        return result.rowcount > 0
    
    def get_by_creator(self, creator_id: str, lesson_id: Optional[str] = None) -> List[Announcement]:
        """Get announcements created by user"""
        if lesson_id:
            query = text("""
                SELECT * FROM lesson_announcement
                WHERE created_by = :creator_id AND lesson_id = :lesson_id
                ORDER BY created_at DESC
            """)
            results = db.session.execute(query, {
                'creator_id': creator_id,
                'lesson_id': lesson_id
            }).fetchall()
        else:
            query = text("""
                SELECT * FROM lesson_announcement
                WHERE created_by = :creator_id
                ORDER BY created_at DESC
            """)
            results = db.session.execute(query, {'creator_id': creator_id}).fetchall()
        
        return [self._row_to_entity(row) for row in results]
    
    def _row_to_entity(self, row) -> Announcement:
        """Convert database row to entity"""
        # Handle both dict and tuple results
        if isinstance(row, dict):
            data = row
        else:
            # Convert Row object to dict
            data = dict(row._mapping) if hasattr(row, '_mapping') else dict(zip(row.keys(), row))
        
        return Announcement(
            id=data['id'],
            lesson_id=data['lesson_id'],
            title=data['title'],
            content=data['content'],
            is_pinned=bool(data['is_pinned']),
            allow_comments=bool(data['allow_comments']),
            scheduled_date=data.get('scheduled_date'),
            is_published=bool(data['is_published']),
            created_by=data['created_by'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            comment_count=data.get('comment_count', 0)
        )


class SQLAlchemyAnnouncementCommentRepository(AnnouncementCommentRepository):
    """SQLAlchemy implementation of AnnouncementCommentRepository"""
    
    def create(self, comment: AnnouncementComment) -> AnnouncementComment:
        """Create new comment"""
        if not comment.id:
            comment.id = str(uuid.uuid4())
        
        if not comment.created_at:
            comment.created_at = datetime.utcnow()
        
        if not comment.updated_at:
            comment.updated_at = datetime.utcnow()
        
        query = text("""
            INSERT INTO announcement_comment (
                id, announcement_id, user_id, content,
                parent_comment_id, is_private, created_at, updated_at
            ) VALUES (
                :id, :announcement_id, :user_id, :content,
                :parent_comment_id, :is_private, :created_at, :updated_at
            )
        """)
        
        db.session.execute(query, {
            'id': comment.id,
            'announcement_id': comment.announcement_id,
            'user_id': comment.user_id,
            'content': comment.content,
            'parent_comment_id': comment.parent_comment_id,
            'is_private': comment.is_private,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at
        })
        db.session.commit()
        
        return comment
    
    def get_by_id(self, comment_id: str) -> Optional[AnnouncementComment]:
        """Get comment by ID"""
        query = text("""
            SELECT c.*, u.username as user_name, u.email as user_email
            FROM announcement_comment c
            LEFT JOIN user u ON c.user_id = u.id
            WHERE c.id = :id
        """)
        
        result = db.session.execute(query, {'id': comment_id}).fetchone()
        
        if not result:
            return None
        
        return self._row_to_entity(result)
    
    def get_by_announcement(self, announcement_id: str, include_private: bool = False) -> List[AnnouncementComment]:
        """Get all comments for announcement"""
        if include_private:
            query = text("""
                SELECT c.*, u.username as user_name, u.email as user_email
                FROM announcement_comment c
                LEFT JOIN user u ON c.user_id = u.id
                WHERE c.announcement_id = :announcement_id
                ORDER BY c.created_at ASC
            """)
        else:
            query = text("""
                SELECT c.*, u.username as user_name, u.email as user_email
                FROM announcement_comment c
                LEFT JOIN user u ON c.user_id = u.id
                WHERE c.announcement_id = :announcement_id AND c.is_private = 0
                ORDER BY c.created_at ASC
            """)
        
        results = db.session.execute(query, {'announcement_id': announcement_id}).fetchall()
        
        return [self._row_to_entity(row) for row in results]
    
    def get_replies(self, parent_comment_id: str) -> List[AnnouncementComment]:
        """Get replies to a comment"""
        query = text("""
            SELECT c.*, u.username as user_name, u.email as user_email
            FROM announcement_comment c
            LEFT JOIN user u ON c.user_id = u.id
            WHERE c.parent_comment_id = :parent_comment_id
            ORDER BY c.created_at ASC
        """)
        
        results = db.session.execute(query, {'parent_comment_id': parent_comment_id}).fetchall()
        
        return [self._row_to_entity(row) for row in results]
    
    def update(self, comment: AnnouncementComment) -> AnnouncementComment:
        """Update comment"""
        comment.updated_at = datetime.utcnow()
        
        query = text("""
            UPDATE announcement_comment
            SET content = :content, is_private = :is_private, updated_at = :updated_at
            WHERE id = :id
        """)
        
        db.session.execute(query, {
            'id': comment.id,
            'content': comment.content,
            'is_private': comment.is_private,
            'updated_at': comment.updated_at
        })
        db.session.commit()
        
        return comment
    
    def delete(self, comment_id: str) -> bool:
        """Delete comment"""
        query = text("""
            DELETE FROM announcement_comment WHERE id = :id
        """)
        
        result = db.session.execute(query, {'id': comment_id})
        db.session.commit()
        
        return result.rowcount > 0
    
    def count_by_announcement(self, announcement_id: str) -> int:
        """Count comments for announcement"""
        query = text("""
            SELECT COUNT(*) as count FROM announcement_comment
            WHERE announcement_id = :announcement_id
        """)
        
        result = db.session.execute(query, {'announcement_id': announcement_id}).fetchone()
        
        return result['count'] if result else 0
    
    def _row_to_entity(self, row) -> AnnouncementComment:
        """Convert database row to entity"""
        if isinstance(row, dict):
            data = row
        else:
            data = dict(row._mapping) if hasattr(row, '_mapping') else dict(zip(row.keys(), row))
        
        return AnnouncementComment(
            id=data['id'],
            announcement_id=data['announcement_id'],
            user_id=data['user_id'],
            content=data['content'],
            parent_comment_id=data.get('parent_comment_id'),
            is_private=bool(data['is_private']),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            user_name=data.get('user_name'),
            user_email=data.get('user_email')
        )

