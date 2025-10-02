"""
Repository Interface: Announcement
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from app.domain.entities.announcement import Announcement, AnnouncementComment


class AnnouncementRepository(ABC):
    """Repository interface for Announcement"""
    
    @abstractmethod
    def create(self, announcement: Announcement) -> Announcement:
        """Create new announcement"""
        pass
    
    @abstractmethod
    def get_by_id(self, announcement_id: str) -> Optional[Announcement]:
        """Get announcement by ID"""
        pass
    
    @abstractmethod
    def get_by_lesson(self, lesson_id: str, include_drafts: bool = False) -> List[Announcement]:
        """Get all announcements for a lesson"""
        pass
    
    @abstractmethod
    def get_pinned(self, lesson_id: str) -> List[Announcement]:
        """Get pinned announcements"""
        pass
    
    @abstractmethod
    def get_scheduled(self, lesson_id: str) -> List[Announcement]:
        """Get scheduled announcements"""
        pass
    
    @abstractmethod
    def update(self, announcement: Announcement) -> Announcement:
        """Update announcement"""
        pass
    
    @abstractmethod
    def delete(self, announcement_id: str) -> bool:
        """Delete announcement"""
        pass
    
    @abstractmethod
    def get_by_creator(self, creator_id: str, lesson_id: Optional[str] = None) -> List[Announcement]:
        """Get announcements created by user"""
        pass


class AnnouncementCommentRepository(ABC):
    """Repository interface for AnnouncementComment"""
    
    @abstractmethod
    def create(self, comment: AnnouncementComment) -> AnnouncementComment:
        """Create new comment"""
        pass
    
    @abstractmethod
    def get_by_id(self, comment_id: str) -> Optional[AnnouncementComment]:
        """Get comment by ID"""
        pass
    
    @abstractmethod
    def get_by_announcement(self, announcement_id: str, include_private: bool = False) -> List[AnnouncementComment]:
        """Get all comments for announcement"""
        pass
    
    @abstractmethod
    def get_replies(self, parent_comment_id: str) -> List[AnnouncementComment]:
        """Get replies to a comment"""
        pass
    
    @abstractmethod
    def update(self, comment: AnnouncementComment) -> AnnouncementComment:
        """Update comment"""
        pass
    
    @abstractmethod
    def delete(self, comment_id: str) -> bool:
        """Delete comment"""
        pass
    
    @abstractmethod
    def count_by_announcement(self, announcement_id: str) -> int:
        """Count comments for announcement"""
        pass

