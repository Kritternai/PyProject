"""
Note repository interface following Repository pattern.
Defines contract for note data access operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.note import Note, NoteType


class NoteRepository(ABC):
    """
    Abstract repository interface for Note entity.
    Defines all data access operations for notes.
    """
    
    @abstractmethod
    def create(self, note: Note) -> Note:
        """
        Create a new note.
        
        Args:
            note: Note entity to create
            
        Returns:
            Created note entity
            
        Raises:
            ValidationException: If note data is invalid
        """
        pass
    
    @abstractmethod
    def get_by_id(self, note_id: str) -> Optional[Note]:
        """
        Get note by ID.
        
        Args:
            note_id: Note ID to search for
            
        Returns:
            Note entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Note]:
        """
        Get notes by user ID.
        
        Args:
            user_id: User ID to search for
            limit: Maximum number of notes to return
            offset: Number of notes to skip
            
        Returns:
            List of note entities
        """
        pass
    
    @abstractmethod
    def update(self, note: Note) -> Note:
        """
        Update existing note.
        
        Args:
            note: Note entity to update
            
        Returns:
            Updated note entity
            
        Raises:
            NotFoundException: If note doesn't exist
            ValidationException: If note data is invalid
        """
        pass
    
    @abstractmethod
    def delete(self, note_id: str) -> bool:
        """
        Delete note by ID.
        
        Args:
            note_id: Note ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def get_by_lesson_id(self, lesson_id: str, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes by lesson ID.
        
        Args:
            lesson_id: Lesson ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of note entities for the lesson
        """
        pass
    
    @abstractmethod
    def get_by_section_id(self, section_id: str, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes by section ID.
        
        Args:
            section_id: Section ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of note entities for the section
        """
        pass
    
    @abstractmethod
    def get_by_note_type(self, user_id: str, note_type: NoteType, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes by type.
        
        Args:
            user_id: User ID to filter by
            note_type: Note type to filter by
            limit: Maximum number of results
            
        Returns:
            List of note entities with specified type
        """
        pass
    
    @abstractmethod
    def get_public_notes(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Note]:
        """
        Get public notes.
        
        Args:
            limit: Maximum number of results
            offset: Number of notes to skip
            
        Returns:
            List of public note entities
        """
        pass
    
    @abstractmethod
    def search(self, user_id: str, query: str, limit: Optional[int] = None) -> List[Note]:
        """
        Search notes by query.
        
        Args:
            user_id: User ID to filter by
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching note entities
        """
        pass
    
    @abstractmethod
    def search_by_tags(self, user_id: str, tags: List[str], limit: Optional[int] = None) -> List[Note]:
        """
        Search notes by tags.
        
        Args:
            user_id: User ID to filter by
            tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of note entities with matching tags
        """
        pass
    
    @abstractmethod
    def get_notes_by_date_range(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Note]:
        """
        Get notes by date range.
        
        Args:
            user_id: User ID to filter by
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of results
            
        Returns:
            List of note entities in date range
        """
        pass
    
    @abstractmethod
    def get_note_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get note statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with note statistics
        """
        pass
    
    @abstractmethod
    def count_by_user(self, user_id: str) -> int:
        """
        Count notes by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total count of notes for user
        """
        pass
    
    @abstractmethod
    def get_recent_notes(self, user_id: str, limit: int = 10) -> List[Note]:
        """
        Get recent notes for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent note entities
        """
        pass
    
    @abstractmethod
    def get_most_viewed_notes(self, user_id: str, limit: int = 10) -> List[Note]:
        """
        Get most viewed notes for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of most viewed note entities
        """
        pass
    
    @abstractmethod
    def get_all_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        pass
