"""
Lesson repository implementation using SQLAlchemy.
Infrastructure layer implementation of LessonRepository interface.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities.lesson import Lesson, LessonStatus, DifficultyLevel, SourcePlatform
from app.domain.interfaces.repositories.lesson_repository import LessonRepository
from ..models.lesson_model import LessonModel
from app import db
from app.shared.exceptions import ValidationException


class LessonRepositoryImpl(LessonRepository):
    """
    SQLAlchemy implementation of LessonRepository interface.
    Handles all database operations for Lesson entity.
    """
    
    def create(self, lesson: Lesson) -> Lesson:
        """
        Create a new lesson.
        
        Args:
            lesson: Lesson entity to create
            
        Returns:
            Created lesson entity
            
        Raises:
            ValidationException: If lesson data is invalid
        """
        try:
            lesson_model = LessonModel.from_domain_entity(lesson)
            db.session.add(lesson_model)
            db.session.commit()
            return lesson_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to create lesson: {str(e)}")
    
    def get_by_id(self, lesson_id: str) -> Optional[Lesson]:
        """
        Get lesson by ID.
        
        Args:
            lesson_id: Lesson ID to search for
            
        Returns:
            Lesson entity if found, None otherwise
        """
        lesson_model = LessonModel.query.filter_by(id=lesson_id).first()
        return lesson_model.to_domain_entity() if lesson_model else None
    
    def get_by_user_id(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Lesson]:
        """
        Get lessons by user ID.
        
        Args:
            user_id: User ID to search for
            limit: Maximum number of lessons to return
            offset: Number of lessons to skip
            
        Returns:
            List of lesson entities
        """
        query = LessonModel.query.filter_by(user_id=user_id).order_by(LessonModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        lesson_models = query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def update(self, lesson: Lesson) -> Lesson:
        """
        Update existing lesson.
        
        Args:
            lesson: Lesson entity to update
            
        Returns:
            Updated lesson entity
            
        Raises:
            NotFoundException: If lesson doesn't exist
            ValidationException: If lesson data is invalid
        """
        try:
            lesson_model = LessonModel.query.filter_by(id=lesson.id).first()
            if not lesson_model:
                from ...shared.exceptions import NotFoundException
                raise NotFoundException("Lesson", lesson.id)
            
            # Update fields
            lesson_model.user_id = lesson.user_id
            lesson_model.title = lesson.title
            lesson_model.description = lesson.description
            lesson_model.status = lesson.status.value
            lesson_model.progress_percentage = lesson.progress_percentage
            lesson_model.difficulty_level = lesson.difficulty_level.value
            lesson_model.estimated_duration = lesson.estimated_duration
            lesson_model.color_theme = lesson.color_theme
            lesson_model.is_favorite = lesson.is_favorite
            lesson_model.source_platform = lesson.source_platform.value
            lesson_model.external_id = lesson.external_id
            lesson_model.external_url = lesson.external_url
            lesson_model.author_name = lesson.author_name
            lesson_model.subject = lesson.subject
            lesson_model.grade_level = lesson.grade_level
            lesson_model.total_sections = lesson.total_sections
            lesson_model.completed_sections = lesson.completed_sections
            lesson_model.total_time_spent = lesson.total_time_spent
            lesson_model.updated_at = lesson.updated_at
            
            db.session.commit()
            return lesson_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            if "NotFoundException" in str(type(e)):
                raise
            raise ValidationException(f"Failed to update lesson: {str(e)}")
    
    def delete(self, lesson_id: str) -> bool:
        """
        Delete lesson by ID.
        
        Args:
            lesson_id: Lesson ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            lesson_model = LessonModel.query.filter_by(id=lesson_id).first()
            if not lesson_model:
                return False
            
            db.session.delete(lesson_model)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to delete lesson: {str(e)}")
    
    def get_by_status(self, user_id: str, status: LessonStatus, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get lessons by status.
        
        Args:
            user_id: User ID to filter by
            status: Lesson status to filter by
            limit: Maximum number of results
            
        Returns:
            List of lesson entities with specified status
        """
        query = LessonModel.query.filter_by(
            user_id=user_id,
            status=status.value
        ).order_by(LessonModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        lesson_models = query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def get_by_difficulty_level(self, user_id: str, difficulty_level: DifficultyLevel, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get lessons by difficulty level.
        
        Args:
            user_id: User ID to filter by
            difficulty_level: Difficulty level to filter by
            limit: Maximum number of results
            
        Returns:
            List of lesson entities with specified difficulty level
        """
        query = LessonModel.query.filter_by(
            user_id=user_id,
            difficulty_level=difficulty_level.value
        ).order_by(LessonModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        lesson_models = query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def get_by_source_platform(self, user_id: str, source_platform: SourcePlatform, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get lessons by source platform.
        
        Args:
            user_id: User ID to filter by
            source_platform: Source platform to filter by
            limit: Maximum number of results
            
        Returns:
            List of lesson entities from specified platform
        """
        query = LessonModel.query.filter_by(
            user_id=user_id,
            source_platform=source_platform.value
        ).order_by(LessonModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        lesson_models = query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def get_favorites(self, user_id: str, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get favorite lessons.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of favorite lesson entities
        """
        query = LessonModel.query.filter_by(
            user_id=user_id,
            is_favorite=True
        ).order_by(LessonModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        lesson_models = query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def search(self, user_id: str, query: str, limit: Optional[int] = None) -> List[Lesson]:
        """
        Search lessons by query.
        
        Args:
            user_id: User ID to filter by
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching lesson entities
        """
        search_query = LessonModel.query.filter(
            db.and_(
                LessonModel.user_id == user_id,
                db.or_(
                    LessonModel.title.contains(query),
                    LessonModel.description.contains(query),
                    LessonModel.author_name.contains(query),
                    LessonModel.subject.contains(query)
                )
            )
        ).order_by(LessonModel.created_at.desc())
        
        if limit:
            search_query = search_query.limit(limit)
        
        lesson_models = search_query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def get_by_external_id(self, external_id: str, source_platform: SourcePlatform) -> Optional[Lesson]:
        """
        Get lesson by external ID and source platform.
        
        Args:
            external_id: External platform ID
            source_platform: Source platform
            
        Returns:
            Lesson entity if found, None otherwise
        """
        lesson_model = LessonModel.query.filter_by(
            external_id=external_id,
            source_platform=source_platform.value
        ).first()
        return lesson_model.to_domain_entity() if lesson_model else None
    
    def exists_by_external_id(self, external_id: str, source_platform: SourcePlatform) -> bool:
        """
        Check if lesson exists by external ID and source platform.
        
        Args:
            external_id: External platform ID
            source_platform: Source platform
            
        Returns:
            True if exists, False otherwise
        """
        return LessonModel.query.filter_by(
            external_id=external_id,
            source_platform=source_platform.value
        ).first() is not None
    
    def get_lessons_by_date_range(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Lesson]:
        """
        Get lessons by date range.
        
        Args:
            user_id: User ID to filter by
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of results
            
        Returns:
            List of lesson entities in date range
        """
        query = LessonModel.query.filter_by(user_id=user_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(LessonModel.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(LessonModel.created_at <= end_dt)
        
        query = query.order_by(LessonModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        lesson_models = query.all()
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
    
    def get_lesson_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get lesson statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with lesson statistics
        """
        total_lessons = LessonModel.query.filter_by(user_id=user_id).count()
        
        # Count by status
        status_counts = db.session.query(
            LessonModel.status,
            db.func.count(LessonModel.id)
        ).filter_by(user_id=user_id).group_by(LessonModel.status).all()
        
        # Count by difficulty
        difficulty_counts = db.session.query(
            LessonModel.difficulty_level,
            db.func.count(LessonModel.id)
        ).filter_by(user_id=user_id).group_by(LessonModel.difficulty_level).all()
        
        # Count favorites
        favorite_count = LessonModel.query.filter_by(
            user_id=user_id,
            is_favorite=True
        ).count()
        
        # Total time spent
        total_time = db.session.query(
            db.func.sum(LessonModel.total_time_spent)
        ).filter_by(user_id=user_id).scalar() or 0
        
        return {
            'total_lessons': total_lessons,
            'status_counts': dict(status_counts),
            'difficulty_counts': dict(difficulty_counts),
            'favorite_count': favorite_count,
            'total_time_spent': total_time
        }
    
    def count_by_user(self, user_id: str) -> int:
        """
        Count lessons by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total count of lessons for user
        """
        return LessonModel.query.filter_by(user_id=user_id).count()
    
    def get_recent_lessons(self, user_id: str, limit: int = 10) -> List[Lesson]:
        """
        Get recent lessons for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent lesson entities
        """
        lesson_models = LessonModel.query.filter_by(
            user_id=user_id
        ).order_by(LessonModel.updated_at.desc()).limit(limit).all()
        
        return [lesson_model.to_domain_entity() for lesson_model in lesson_models]
