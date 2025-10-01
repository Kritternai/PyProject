"""
Note service interface following Service Layer pattern.
Defines contract for note business operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.note import Note, NoteType


class NoteService(ABC):
    """
    Abstract service interface for Note business operations.
    Defines all business logic operations for notes.
    """
    
    @abstractmethod
    def create_note(
        self,
        user_id: str,
        title: str,
        content: str,
        note_type: NoteType = NoteType.TEXT,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False
    ) -> Note:
        """
        Create a new note with business validation.
        
        Args:
            user_id: ID of the user creating the note
            title: Note title
            content: Note content
            note_type: Type of note
            lesson_id: Associated lesson ID
            section_id: Associated section ID
            tags: List of tags
            is_public: Whether note is public
            
        Returns:
            Created note entity
            
        Raises:
            ValidationException: If note data is invalid
            BusinessLogicException: If business rules are violated
        """
        pass
    
    @abstractmethod
    def get_note_by_id(self, note_id: str, user_id: str) -> Optional[Note]:
        """
        Get note by ID with user authorization.
        
        Args:
            note_id: Note ID to search for
            user_id: User ID for authorization
            
        Returns:
            Note entity if found and authorized, None otherwise
        """
        pass
    
    @abstractmethod
    def get_user_notes(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Note]:
        """
        Get notes for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of notes
            offset: Number of notes to skip
            
        Returns:
            List of note entities
        """
        pass
    
    @abstractmethod
    def update_note(
        self,
        note_id: str,
        user_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        note_type: Optional[NoteType] = None,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: Optional[bool] = None
    ) -> Note:
        """
        Update note with business validation.
        
        Args:
            note_id: Note ID to update
            user_id: User ID for authorization
            title: New title
            content: New content
            note_type: New note type
            lesson_id: New lesson ID
            section_id: New section ID
            tags: New tags
            is_public: New public status
            
        Returns:
            Updated note entity
            
        Raises:
            NotFoundException: If note doesn't exist
            ValidationException: If data is invalid
            AuthorizationException: If user not authorized
        """
        pass
    
    @abstractmethod
    def delete_note(self, note_id: str, user_id: str) -> bool:
        """
        Delete note with user authorization.
        
        Args:
            note_id: Note ID to delete
            user_id: User ID for authorization
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            AuthorizationException: If user not authorized
        """
        pass
    
    @abstractmethod
    def get_notes_by_lesson(self, lesson_id: str, user_id: str, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes for a specific lesson.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID for authorization
            limit: Maximum number of results
            
        Returns:
            List of note entities for the lesson
        """
        pass
    
    @abstractmethod
    def get_notes_by_section(self, section_id: str, user_id: str, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes for a specific section.
        
        Args:
            section_id: Section ID
            user_id: User ID for authorization
            limit: Maximum number of results
            
        Returns:
            List of note entities for the section
        """
        pass
    
    @abstractmethod
    def search_notes(
        self,
        user_id: str,
        query: str,
        limit: Optional[int] = None
    ) -> List[Note]:
        """
        Search notes by query.
        
        Args:
            user_id: User ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching note entities
        """
        pass
    
    @abstractmethod
    def search_notes_by_tags(
        self,
        user_id: str,
        tags: List[str],
        limit: Optional[int] = None
    ) -> List[Note]:
        """
        Search notes by tags.
        
        Args:
            user_id: User ID
            tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of note entities with matching tags
        """
        pass
    
    @abstractmethod
    def get_notes_by_type(
        self,
        user_id: str,
        note_type: NoteType,
        limit: Optional[int] = None
    ) -> List[Note]:
        """
        Get notes by type.
        
        Args:
            user_id: User ID
            note_type: Note type
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
    def toggle_public_status(self, note_id: str, user_id: str) -> Note:
        """
        Toggle note public status.
        
        Args:
            note_id: Note ID
            user_id: User ID for authorization
            
        Returns:
            Updated note entity
            
        Raises:
            NotFoundException: If note doesn't exist
            AuthorizationException: If user not authorized
        """
        pass
    
    @abstractmethod
    def add_tag(self, note_id: str, user_id: str, tag: str) -> Note:
        """
        Add tag to note.
        
        Args:
            note_id: Note ID
            user_id: User ID for authorization
            tag: Tag to add
            
        Returns:
            Updated note entity
            
        Raises:
            NotFoundException: If note doesn't exist
            ValidationException: If tag is invalid
            AuthorizationException: If user not authorized
        """
        pass
    
    @abstractmethod
    def remove_tag(self, note_id: str, user_id: str, tag: str) -> Note:
        """
        Remove tag from note.
        
        Args:
            note_id: Note ID
            user_id: User ID for authorization
            tag: Tag to remove
            
        Returns:
            Updated note entity
            
        Raises:
            NotFoundException: If note doesn't exist
            AuthorizationException: If user not authorized
        """
        pass
    
    @abstractmethod
    def increment_view_count(self, note_id: str) -> None:
        """
        Increment note view count.
        
        Args:
            note_id: Note ID
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
    def get_all_user_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        pass
