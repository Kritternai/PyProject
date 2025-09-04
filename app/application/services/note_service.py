"""
Note service implementation following Service Layer pattern.
Implements business logic for note operations.
"""

from typing import List, Optional, Dict, Any
from app.domain.entities.note import Note, NoteType
from app.domain.interfaces.services.note_service import NoteService
from app.domain.interfaces.repositories.note_repository import NoteRepository
from app.shared.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException,
    AuthorizationException
)


class NoteServiceImpl(NoteService):
    """
    Implementation of NoteService interface.
    Contains business logic for note operations.
    """
    
    def __init__(self, note_repository: NoteRepository):
        """
        Initialize note service with repository dependency.
        
        Args:
            note_repository: Note repository implementation
        """
        self._note_repository = note_repository
    
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
        # Business validation
        if tags and len(tags) > 20:
            raise BusinessLogicException(
                "Cannot have more than 20 tags",
                rule="tag_limit"
            )
        
        # Create note entity
        note = Note(
            user_id=user_id,
            title=title,
            content=content,
            note_type=note_type,
            lesson_id=lesson_id,
            section_id=section_id,
            tags=tags or [],
            is_public=is_public
        )
        
        # Save to repository
        return self._note_repository.create(note)
    
    def get_note_by_id(self, note_id: str, user_id: str) -> Optional[Note]:
        """
        Get note by ID with user authorization.
        
        Args:
            note_id: Note ID to search for
            user_id: User ID for authorization
            
        Returns:
            Note entity if found and authorized, None otherwise
        """
        note = self._note_repository.get_by_id(note_id)
        if note and (note.user_id == user_id or note.is_public):
            return note
        return None
    
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
        return self._note_repository.get_by_user_id(user_id, limit=limit, offset=offset)
    
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
        note = self._note_repository.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)
        
        if note.user_id != user_id:
            raise AuthorizationException("You can only update your own notes")
        
        # Update fields
        if title is not None:
            note.update_title(title)
        
        if content is not None:
            note.update_content(content)
        
        if note_type is not None:
            note.change_note_type(note_type)
        
        if lesson_id is not None:
            note.set_lesson_association(lesson_id)
        
        if section_id is not None:
            note.set_section_association(section_id)
        
        if tags is not None:
            note.set_tags(tags)
        
        if is_public is not None:
            note.set_public(is_public)
        
        return self._note_repository.update(note)
    
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
        note = self._note_repository.get_by_id(note_id)
        if note and note.user_id != user_id:
            raise AuthorizationException("You can only delete your own notes")
        
        return self._note_repository.delete(note_id)
    
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
        notes = self._note_repository.get_by_lesson_id(lesson_id, limit=limit)
        # Filter by user authorization
        return [note for note in notes if note.user_id == user_id or note.is_public]
    
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
        notes = self._note_repository.get_by_section_id(section_id, limit=limit)
        # Filter by user authorization
        return [note for note in notes if note.user_id == user_id or note.is_public]
    
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
        return self._note_repository.search(user_id, query, limit=limit)
    
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
        return self._note_repository.search_by_tags(user_id, tags, limit=limit)
    
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
        return self._note_repository.get_by_note_type(user_id, note_type, limit=limit)
    
    def get_public_notes(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Note]:
        """
        Get public notes.
        
        Args:
            limit: Maximum number of results
            offset: Number of notes to skip
            
        Returns:
            List of public note entities
        """
        return self._note_repository.get_public_notes(limit=limit, offset=offset)
    
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
        note = self._note_repository.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)
        
        if note.user_id != user_id:
            raise AuthorizationException("You can only update your own notes")
        
        note.toggle_public()
        return self._note_repository.update(note)
    
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
        note = self._note_repository.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)
        
        if note.user_id != user_id:
            raise AuthorizationException("You can only update your own notes")
        
        note.add_tag(tag)
        return self._note_repository.update(note)
    
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
        note = self._note_repository.get_by_id(note_id)
        if not note:
            raise NotFoundException("Note", note_id)
        
        if note.user_id != user_id:
            raise AuthorizationException("You can only update your own notes")
        
        note.remove_tag(tag)
        return self._note_repository.update(note)
    
    def increment_view_count(self, note_id: str) -> None:
        """
        Increment note view count.
        
        Args:
            note_id: Note ID
        """
        note = self._note_repository.get_by_id(note_id)
        if note:
            note.increment_view_count()
            self._note_repository.update(note)
    
    def get_note_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get note statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with note statistics
        """
        return self._note_repository.get_note_statistics(user_id)
    
    def get_recent_notes(self, user_id: str, limit: int = 10) -> List[Note]:
        """
        Get recent notes for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent note entities
        """
        return self._note_repository.get_recent_notes(user_id, limit=limit)
    
    def get_most_viewed_notes(self, user_id: str, limit: int = 10) -> List[Note]:
        """
        Get most viewed notes for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of most viewed note entities
        """
        return self._note_repository.get_most_viewed_notes(user_id, limit=limit)
    
    def get_all_user_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        return self._note_repository.get_all_tags(user_id)
