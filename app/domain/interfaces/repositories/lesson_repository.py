"""
Lesson repository interface following Repository pattern.
Defines contract for lesson data access operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.lesson import Lesson, LessonStatus, DifficultyLevel, SourcePlatform


class LessonRepository(ABC):
    """
    Abstract repository interface for Lesson entity.
    Defines all data access operations for lessons.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_by_id(self, lesson_id: str) -> Optional[Lesson]:
        """
        Get lesson by ID.
        
        Args:
            lesson_id: Lesson ID to search for
            
        Returns:
            Lesson entity if found, None otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def delete(self, lesson_id: str) -> bool:
        """
        Delete lesson by ID.
        
        Args:
            lesson_id: Lesson ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_favorites(self, user_id: str, limit: Optional[int] = None) -> List[Lesson]:
        """
        Get favorite lessons.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of favorite lesson entities
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_by_external_id(self, external_id: str, source_platform: SourcePlatform) -> Optional[Lesson]:
        """
        Get lesson by external ID and source platform.
        
        Args:
            external_id: External platform ID
            source_platform: Source platform
            
        Returns:
            Lesson entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def exists_by_external_id(self, external_id: str, source_platform: SourcePlatform) -> bool:
        """
        Check if lesson exists by external ID and source platform.
        
        Args:
            external_id: External platform ID
            source_platform: Source platform
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
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
    def count_by_user(self, user_id: str) -> int:
        """
        Count lessons by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total count of lessons for user
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
