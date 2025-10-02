"""
Dependency Injection Container: Announcement
"""
from app.infrastructure.database.announcement_repository import (
    SQLAlchemyAnnouncementRepository,
    SQLAlchemyAnnouncementCommentRepository
)
from app.application.services.announcement_service import (
    AnnouncementServiceImpl,
    AnnouncementCommentServiceImpl
)


# Singleton instances
_announcement_repo = None
_comment_repo = None
_announcement_service = None
_comment_service = None


def get_announcement_repository():
    """Get announcement repository instance"""
    global _announcement_repo
    if _announcement_repo is None:
        _announcement_repo = SQLAlchemyAnnouncementRepository()
    return _announcement_repo


def get_comment_repository():
    """Get comment repository instance"""
    global _comment_repo
    if _comment_repo is None:
        _comment_repo = SQLAlchemyAnnouncementCommentRepository()
    return _comment_repo


def get_announcement_service():
    """Get announcement service instance"""
    global _announcement_service
    if _announcement_service is None:
        _announcement_service = AnnouncementServiceImpl(
            announcement_repo=get_announcement_repository(),
            comment_repo=get_comment_repository()
        )
    return _announcement_service


def get_comment_service():
    """Get comment service instance"""
    global _comment_service
    if _comment_service is None:
        _comment_service = AnnouncementCommentServiceImpl(
            comment_repo=get_comment_repository()
        )
    return _comment_service

