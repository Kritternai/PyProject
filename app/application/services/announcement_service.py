"""
Application Service: Announcement
Business logic for announcement management
"""
from typing import List, Optional
from datetime import datetime
import uuid

from app.domain.entities.announcement import Announcement, AnnouncementComment
from app.domain.interfaces.announcement_repository import (
    AnnouncementRepository,
    AnnouncementCommentRepository
)


class AnnouncementService:
    """
    Service for announcement management
    
    Handles:
    - Creating and managing announcements
    - Pinning/Unpinning
    - Scheduling
    - Publishing
    """
    
    def __init__(
        self,
        announcement_repo: AnnouncementRepository,
        comment_repo: AnnouncementCommentRepository
    ):
        self._announcement_repo = announcement_repo
        self._comment_repo = comment_repo
    
    # ========================================
    # ANNOUNCEMENT CRUD
    # ========================================
    
    def create_announcement(
        self,
        lesson_id: str,
        title: str,
        content: str,
        created_by: str,
        is_pinned: bool = False,
        allow_comments: bool = True,
        scheduled_date: Optional[datetime] = None,
        is_published: bool = True
    ) -> Announcement:
        """
        Create new announcement
        
        Args:
            lesson_id: ID of the lesson/class
            title: Announcement title
            content: Announcement content
            created_by: User ID of creator
            is_pinned: Pin to top
            allow_comments: Allow comments
            scheduled_date: Schedule for future
            is_published: Publish immediately
        
        Returns:
            Created announcement
        """
        announcement = Announcement(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            title=title,
            content=content,
            is_pinned=is_pinned,
            allow_comments=allow_comments,
            scheduled_date=scheduled_date,
            is_published=is_published,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return self._announcement_repo.create(announcement)
    
    def get_announcement(self, announcement_id: str) -> Optional[Announcement]:
        """Get announcement by ID"""
        return self._announcement_repo.get_by_id(announcement_id)
    
    def get_lesson_announcements(
        self,
        lesson_id: str,
        include_drafts: bool = False
    ) -> List[Announcement]:
        """
        Get all announcements for a lesson
        
        Returns announcements sorted by:
        1. Pinned first
        2. Then by creation date (newest first)
        """
        return self._announcement_repo.get_by_lesson(lesson_id, include_drafts)
    
    def update_announcement(
        self,
        announcement_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Announcement:
        """Update announcement content"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        if title is not None and content is not None:
            announcement.update_content(title, content)
        
        return self._announcement_repo.update(announcement)
    
    def delete_announcement(self, announcement_id: str) -> bool:
        """Delete announcement"""
        return self._announcement_repo.delete(announcement_id)
    
    # ========================================
    # ANNOUNCEMENT ACTIONS
    # ========================================
    
    def pin_announcement(self, announcement_id: str) -> Announcement:
        """Pin announcement to top"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        announcement.pin()
        return self._announcement_repo.update(announcement)
    
    def unpin_announcement(self, announcement_id: str) -> Announcement:
        """Unpin announcement"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        announcement.unpin()
        return self._announcement_repo.update(announcement)
    
    def publish_announcement(self, announcement_id: str) -> Announcement:
        """Publish announcement"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        announcement.publish()
        return self._announcement_repo.update(announcement)
    
    def unpublish_announcement(self, announcement_id: str) -> Announcement:
        """Unpublish announcement (make draft)"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        announcement.unpublish()
        return self._announcement_repo.update(announcement)
    
    def schedule_announcement(
        self,
        announcement_id: str,
        scheduled_date: datetime
    ) -> Announcement:
        """Schedule announcement for future"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        announcement.schedule(scheduled_date)
        return self._announcement_repo.update(announcement)
    
    def toggle_comments(self, announcement_id: str) -> Announcement:
        """Toggle comments on/off"""
        announcement = self._announcement_repo.get_by_id(announcement_id)
        
        if not announcement:
            raise ValueError(f"Announcement {announcement_id} not found")
        
        if announcement.allow_comments:
            announcement.disable_comments()
        else:
            announcement.enable_comments()
        
        return self._announcement_repo.update(announcement)
    
    # ========================================
    # QUERIES
    # ========================================
    
    def get_pinned_announcements(self, lesson_id: str) -> List[Announcement]:
        """Get all pinned announcements"""
        return self._announcement_repo.get_pinned(lesson_id)
    
    def get_scheduled_announcements(self, lesson_id: str) -> List[Announcement]:
        """Get scheduled announcements"""
        return self._announcement_repo.get_scheduled(lesson_id)
    
    def get_user_announcements(
        self,
        user_id: str,
        lesson_id: Optional[str] = None
    ) -> List[Announcement]:
        """Get announcements created by user"""
        return self._announcement_repo.get_by_creator(user_id, lesson_id)


class AnnouncementCommentService:
    """
    Service for announcement comments
    
    Handles:
    - Creating and managing comments
    - Nested replies
    - Private comments
    """
    
    def __init__(self, comment_repo: AnnouncementCommentRepository):
        self._comment_repo = comment_repo
    
    # ========================================
    # COMMENT CRUD
    # ========================================
    
    def create_comment(
        self,
        announcement_id: str,
        user_id: str,
        content: str,
        parent_comment_id: Optional[str] = None,
        is_private: bool = False
    ) -> AnnouncementComment:
        """
        Create new comment
        
        Args:
            announcement_id: ID of announcement
            user_id: ID of user posting comment
            content: Comment content
            parent_comment_id: Parent comment (for replies)
            is_private: Private comment (teachers only)
        
        Returns:
            Created comment
        """
        comment = AnnouncementComment(
            id=str(uuid.uuid4()),
            announcement_id=announcement_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id,
            is_private=is_private,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return self._comment_repo.create(comment)
    
    def get_comment(self, comment_id: str) -> Optional[AnnouncementComment]:
        """Get comment by ID"""
        return self._comment_repo.get_by_id(comment_id)
    
    def get_announcement_comments(
        self,
        announcement_id: str,
        include_private: bool = False
    ) -> List[AnnouncementComment]:
        """
        Get all comments for announcement
        
        Args:
            announcement_id: Announcement ID
            include_private: Include private comments (teachers only)
        
        Returns:
            List of comments (sorted by creation date)
        """
        return self._comment_repo.get_by_announcement(announcement_id, include_private)
    
    def get_comment_replies(self, parent_comment_id: str) -> List[AnnouncementComment]:
        """Get replies to a comment"""
        return self._comment_repo.get_replies(parent_comment_id)
    
    def update_comment(self, comment_id: str, content: str) -> AnnouncementComment:
        """Update comment content"""
        comment = self._comment_repo.get_by_id(comment_id)
        
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        
        comment.update_content(content)
        return self._comment_repo.update(comment)
    
    def delete_comment(self, comment_id: str) -> bool:
        """Delete comment"""
        return self._comment_repo.delete(comment_id)
    
    def count_comments(self, announcement_id: str) -> int:
        """Count comments for announcement"""
        return self._comment_repo.count_by_announcement(announcement_id)
    
    # ========================================
    # COMMENT ACTIONS
    # ========================================
    
    def mark_private(self, comment_id: str) -> AnnouncementComment:
        """Mark comment as private"""
        comment = self._comment_repo.get_by_id(comment_id)
        
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        
        comment.mark_private()
        return self._comment_repo.update(comment)
    
    def mark_public(self, comment_id: str) -> AnnouncementComment:
        """Mark comment as public"""
        comment = self._comment_repo.get_by_id(comment_id)
        
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        
        comment.mark_public()
        return self._comment_repo.update(comment)


# ========================================
# SERVICE IMPLEMENTATIONS
# ========================================

class AnnouncementServiceImpl(AnnouncementService):
    """Default implementation of AnnouncementService"""
    pass


class AnnouncementCommentServiceImpl(AnnouncementCommentService):
    """Default implementation of AnnouncementCommentService"""
    pass

