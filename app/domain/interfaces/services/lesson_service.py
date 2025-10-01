"""
Lesson service interface following Service Layer pattern.
Defines contract for lesson business operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.lesson import Lesson, LessonStatus, DifficultyLevel, SourcePlatform


class LessonService(ABC):
    """
    Abstract service interface for Lesson business operations.
    Defines all business logic operations for lessons.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_lesson_by_id(self, lesson_id: str, user_id: str) -> Optional[Lesson]:
        """
        Get lesson by ID with user authorization.
        
        Args:
            lesson_id: Lesson ID to search for
            user_id: User ID for authorization
            
        Returns:
            Lesson entity if found and authorized, None otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_favorite_lessons(self, user_id: str, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get favorite lessons.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of favorite lesson entities
        """
        pass
    
    @abstractmethod
    def get_lesson_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get lesson statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with lesson statistics
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_recent_lessons(self, user_id: str, limit: int = 10) -> List[Lesson]:
        """
        Get recent lessons for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent lesson entities
        """
        pass
