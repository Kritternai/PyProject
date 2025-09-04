"""
Lesson service implementation following Service Layer pattern.
Implements business logic for lesson operations.
"""

from typing import List, Optional, Dict, Any
from app.domain.entities.lesson import Lesson, LessonStatus, DifficultyLevel, SourcePlatform
from app.domain.interfaces.services.lesson_service import LessonService
from app.domain.interfaces.repositories.lesson_repository import LessonRepository
from app.shared.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException,
    AuthorizationException
)


class LessonServiceImpl(LessonService):
    """
    Implementation of LessonService interface.
    Contains business logic for lesson operations.
    """
    
    def __init__(self, lesson_repository: LessonRepository):
        """
        Initialize lesson service with repository dependency.
        
        Args:
            lesson_repository: Lesson repository implementation
        """
        self._lesson_repository = lesson_repository
    
    def create_lesson(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER,
        estimated_duration: Optional[int] = None,
        color_theme: int = 1,
        source_platform: SourcePlatform = SourcePlatform.MANUAL,
        external_id: Optional[str] = None,
        external_url: Optional[str] = None,
        author_name: Optional[str] = None,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> Lesson:
        """
        Create a new lesson with business validation.
        
        Args:
            user_id: ID of the user creating the lesson
            title: Lesson title
            description: Lesson description
            difficulty_level: Difficulty level
            estimated_duration: Estimated duration in minutes
            color_theme: Color theme (1-6)
            source_platform: Source platform
            external_id: External platform ID
            external_url: External platform URL
            author_name: Author name
            subject: Subject
            grade_level: Grade level
            
        Returns:
            Created lesson entity
            
        Raises:
            ValidationException: If lesson data is invalid
            BusinessLogicException: If business rules are violated
        """
        # Business validation
        if source_platform != SourcePlatform.MANUAL and not external_id:
            raise BusinessLogicException(
                "External ID is required for non-manual lessons",
                rule="external_id_required"
            )
        
        # Check if lesson with same external ID already exists
        if external_id and self._lesson_repository.exists_by_external_id(external_id, source_platform):
            raise BusinessLogicException(
                f"Lesson with external ID '{external_id}' already exists",
                rule="duplicate_external_id"
            )
        
        # Create lesson entity
        lesson = Lesson(
            user_id=user_id,
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            estimated_duration=estimated_duration,
            color_theme=color_theme,
            source_platform=source_platform,
            external_id=external_id,
            external_url=external_url,
            author_name=author_name,
            subject=subject,
            grade_level=grade_level
        )
        
        # Save to repository
        return self._lesson_repository.create(lesson)
    
    def get_lesson_by_id(self, lesson_id: str, user_id: str) -> Optional[Lesson]:
        """
        Get lesson by ID with user authorization.
        
        Args:
            lesson_id: Lesson ID to search for
            user_id: User ID for authorization
            
        Returns:
            Lesson entity if found and authorized, None otherwise
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if lesson and lesson.user_id == user_id:
            return lesson
        return None
    
    def get_user_lessons(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Lesson]:
        """
        Get lessons for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of lessons
            offset: Number of lessons to skip
            
        Returns:
            List of lesson entities
        """
        return self._lesson_repository.get_by_user_id(user_id, limit=limit, offset=offset)
    
    def update_lesson(
        self,
        lesson_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        estimated_duration: Optional[int] = None,
        color_theme: Optional[int] = None,
        author_name: Optional[str] = None,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> Lesson:
        """
        Update lesson with business validation.
        
        Args:
            lesson_id: Lesson ID to update
            user_id: User ID for authorization
            title: New title
            description: New description
            difficulty_level: New difficulty level
            estimated_duration: New estimated duration
            color_theme: New color theme
            author_name: New author name
            subject: New subject
            grade_level: New grade level
            
        Returns:
            Updated lesson entity
            
        Raises:
            NotFoundException: If lesson doesn't exist
            ValidationException: If data is invalid
            AuthorizationException: If user not authorized
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        
        if lesson.user_id != user_id:
            raise AuthorizationException("You can only update your own lessons")
        
        # Update fields
        if title is not None:
            lesson.update_title(title)
        
        if description is not None:
            lesson.update_description(description)
        
        if difficulty_level is not None:
            lesson.update_difficulty_level(difficulty_level)
        
        if estimated_duration is not None:
            lesson.update_estimated_duration(estimated_duration)
        
        if color_theme is not None:
            if color_theme < 1 or color_theme > 6:
                raise ValidationException("Color theme must be between 1 and 6", field="color_theme")
            lesson._color_theme = color_theme
            lesson._updated_at = lesson._updated_at
        
        if author_name is not None:
            lesson._author_name = author_name
            lesson._updated_at = lesson._updated_at
        
        if subject is not None:
            lesson._subject = subject
            lesson._updated_at = lesson._updated_at
        
        if grade_level is not None:
            lesson._grade_level = grade_level
            lesson._updated_at = lesson._updated_at
        
        return self._lesson_repository.update(lesson)
    
    def delete_lesson(self, lesson_id: str, user_id: str) -> bool:
        """
        Delete lesson with user authorization.
        
        Args:
            lesson_id: Lesson ID to delete
            user_id: User ID for authorization
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            AuthorizationException: If user not authorized
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if lesson and lesson.user_id != user_id:
            raise AuthorizationException("You can only delete your own lessons")
        
        return self._lesson_repository.delete(lesson_id)
    
    def change_lesson_status(self, lesson_id: str, user_id: str, status: LessonStatus) -> Lesson:
        """
        Change lesson status.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID for authorization
            status: New status
            
        Returns:
            Updated lesson entity
            
        Raises:
            NotFoundException: If lesson doesn't exist
            AuthorizationException: If user not authorized
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        
        if lesson.user_id != user_id:
            raise AuthorizationException("You can only update your own lessons")
        
        lesson.change_status(status)
        return self._lesson_repository.update(lesson)
    
    def update_lesson_progress(self, lesson_id: str, user_id: str, percentage: int) -> Lesson:
        """
        Update lesson progress.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID for authorization
            percentage: Progress percentage (0-100)
            
        Returns:
            Updated lesson entity
            
        Raises:
            NotFoundException: If lesson doesn't exist
            ValidationException: If percentage is invalid
            AuthorizationException: If user not authorized
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        
        if lesson.user_id != user_id:
            raise AuthorizationException("You can only update your own lessons")
        
        lesson.update_progress(percentage)
        return self._lesson_repository.update(lesson)
    
    def toggle_favorite(self, lesson_id: str, user_id: str) -> Lesson:
        """
        Toggle lesson favorite status.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID for authorization
            
        Returns:
            Updated lesson entity
            
        Raises:
            NotFoundException: If lesson doesn't exist
            AuthorizationException: If user not authorized
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        
        if lesson.user_id != user_id:
            raise AuthorizationException("You can only update your own lessons")
        
        lesson.toggle_favorite()
        return self._lesson_repository.update(lesson)
    
    def add_time_spent(self, lesson_id: str, user_id: str, minutes: int) -> Lesson:
        """
        Add time spent on lesson.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID for authorization
            minutes: Minutes to add
            
        Returns:
            Updated lesson entity
            
        Raises:
            NotFoundException: If lesson doesn't exist
            ValidationException: If minutes is invalid
            AuthorizationException: If user not authorized
        """
        lesson = self._lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        
        if lesson.user_id != user_id:
            raise AuthorizationException("You can only update your own lessons")
        
        lesson.add_time_spent(minutes)
        return self._lesson_repository.update(lesson)
    
    def search_lessons(
        self,
        user_id: str,
        query: str,
        limit: Optional[int] = None
    ) -> List[Lesson]:
        """
        Search lessons by query.
        
        Args:
            user_id: User ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching lesson entities
        """
        return self._lesson_repository.search(user_id, query, limit=limit)
    
    def get_lessons_by_status(
        self,
        user_id: str,
        status: LessonStatus,
        limit: Optional[int] = None
    ) -> List[Lesson]:
        """
        Get lessons by status.
        
        Args:
            user_id: User ID
            status: Lesson status
            limit: Maximum number of results
            
        Returns:
            List of lesson entities with specified status
        """
        return self._lesson_repository.get_by_status(user_id, status, limit=limit)
    
    def get_lessons_by_difficulty(
        self,
        user_id: str,
        difficulty_level: DifficultyLevel,
        limit: Optional[int] = None
    ) -> List[Lesson]:
        """
        Get lessons by difficulty level.
        
        Args:
            user_id: User ID
            difficulty_level: Difficulty level
            limit: Maximum number of results
            
        Returns:
            List of lesson entities with specified difficulty
        """
        return self._lesson_repository.get_by_difficulty_level(user_id, difficulty_level, limit=limit)
    
    def get_favorite_lessons(self, user_id: str, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get favorite lessons.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of favorite lesson entities
        """
        return self._lesson_repository.get_favorites(user_id, limit=limit)
    
    def get_lesson_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get lesson statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with lesson statistics
        """
        return self._lesson_repository.get_lesson_statistics(user_id)
    
    def import_external_lesson(
        self,
        user_id: str,
        title: str,
        source_platform: SourcePlatform,
        external_id: str,
        external_url: Optional[str] = None,
        description: Optional[str] = None,
        author_name: Optional[str] = None,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> Lesson:
        """
        Import lesson from external platform.
        
        Args:
            user_id: User ID
            title: Lesson title
            source_platform: Source platform
            external_id: External platform ID
            external_url: External platform URL
            description: Lesson description
            author_name: Author name
            subject: Subject
            grade_level: Grade level
            
        Returns:
            Created lesson entity
            
        Raises:
            ValidationException: If data is invalid
            BusinessLogicException: If lesson already exists
        """
        # Check if lesson already exists
        if self._lesson_repository.exists_by_external_id(external_id, source_platform):
            raise BusinessLogicException(
                f"Lesson with external ID '{external_id}' already exists",
                rule="duplicate_external_lesson"
            )
        
        return self.create_lesson(
            user_id=user_id,
            title=title,
            description=description,
            source_platform=source_platform,
            external_id=external_id,
            external_url=external_url,
            author_name=author_name,
            subject=subject,
            grade_level=grade_level
        )
    
    def get_recent_lessons(self, user_id: str, limit: int = 10) -> List[Lesson]:
        """
        Get recent lessons for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent lesson entities
        """
        return self._lesson_repository.get_recent_lessons(user_id, limit=limit)
