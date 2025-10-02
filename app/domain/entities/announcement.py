"""
Domain Entity: Announcement
ประกาศในคลาส (เหมือน Google Classroom Stream)
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class AnnouncementStatus(Enum):
    """Status of announcement"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


@dataclass
class Announcement:
    """
    Announcement entity (ประกาศในคลาส)
    
    Business Rules:
    - Only teachers/assistants can create announcements
    - Can be pinned to top
    - Can be scheduled for future publishing
    - Comments can be disabled
    """
    
    # Identity
    id: str
    lesson_id: str
    
    # Content
    title: str
    content: str
    
    # Settings
    is_pinned: bool = False
    allow_comments: bool = True
    
    # Schedule
    scheduled_date: Optional[datetime] = None
    is_published: bool = True
    
    # Metadata
    created_by: str = None
    created_at: datetime = None
    updated_at: datetime = None
    
    # Computed properties
    comment_count: int = 0
    
    def __post_init__(self):
        """Validate announcement data"""
        if not self.title or not self.title.strip():
            raise ValueError("Announcement title cannot be empty")
        
        if not self.content or not self.content.strip():
            raise ValueError("Announcement content cannot be empty")
        
        if not self.lesson_id:
            raise ValueError("Lesson ID is required")
        
        if not self.created_by:
            raise ValueError("Creator ID is required")
    
    @property
    def status(self) -> AnnouncementStatus:
        """Get announcement status"""
        if not self.is_published:
            return AnnouncementStatus.DRAFT
        
        if self.scheduled_date and self.scheduled_date > datetime.utcnow():
            return AnnouncementStatus.SCHEDULED
        
        return AnnouncementStatus.PUBLISHED
    
    @property
    def is_scheduled(self) -> bool:
        """Check if announcement is scheduled"""
        return bool(self.scheduled_date and self.scheduled_date > datetime.utcnow())
    
    def pin(self):
        """Pin announcement to top"""
        self.is_pinned = True
        self.updated_at = datetime.utcnow()
    
    def unpin(self):
        """Unpin announcement"""
        self.is_pinned = False
        self.updated_at = datetime.utcnow()
    
    def publish(self):
        """Publish announcement"""
        self.is_published = True
        self.updated_at = datetime.utcnow()
    
    def unpublish(self):
        """Unpublish announcement (draft)"""
        self.is_published = False
        self.updated_at = datetime.utcnow()
    
    def schedule(self, scheduled_date: datetime):
        """Schedule announcement for future"""
        if scheduled_date <= datetime.utcnow():
            raise ValueError("Scheduled date must be in the future")
        
        self.scheduled_date = scheduled_date
        self.is_published = True
        self.updated_at = datetime.utcnow()
    
    def enable_comments(self):
        """Enable comments"""
        self.allow_comments = True
        self.updated_at = datetime.utcnow()
    
    def disable_comments(self):
        """Disable comments"""
        self.allow_comments = False
        self.updated_at = datetime.utcnow()
    
    def update_content(self, title: str, content: str):
        """Update announcement content"""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        self.title = title.strip()
        self.content = content.strip()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'allow_comments': self.allow_comments,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'is_published': self.is_published,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comment_count': self.comment_count,
            'status': self.status.value
        }


@dataclass
class AnnouncementComment:
    """
    Comment on announcement
    
    Business Rules:
    - Can be nested (replies)
    - Can be private (only visible to teachers)
    - Only members can comment
    """
    
    # Identity
    id: str
    announcement_id: str
    user_id: str
    
    # Content
    content: str
    
    # Settings
    parent_comment_id: Optional[str] = None
    is_private: bool = False
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    
    # User info (denormalized for display)
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    
    def __post_init__(self):
        """Validate comment data"""
        if not self.content or not self.content.strip():
            raise ValueError("Comment content cannot be empty")
        
        if not self.announcement_id:
            raise ValueError("Announcement ID is required")
        
        if not self.user_id:
            raise ValueError("User ID is required")
    
    @property
    def is_reply(self) -> bool:
        """Check if this is a reply"""
        return bool(self.parent_comment_id)
    
    def update_content(self, content: str):
        """Update comment content"""
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        self.content = content.strip()
        self.updated_at = datetime.utcnow()
    
    def mark_private(self):
        """Mark as private (teachers only)"""
        self.is_private = True
        self.updated_at = datetime.utcnow()
    
    def mark_public(self):
        """Mark as public"""
        self.is_private = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'user_id': self.user_id,
            'content': self.content,
            'parent_comment_id': self.parent_comment_id,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'is_reply': self.is_reply
        }

