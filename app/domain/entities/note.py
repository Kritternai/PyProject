"""
Note domain entity following Domain-Driven Design principles.
Pure business object with no external dependencies.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from ..interfaces.entity import Entity


class NoteType(Enum):
    """Note type enumeration."""
    TEXT = "text"
    MARKDOWN = "markdown"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Note(Entity):
    """
    Note domain entity representing a note in the system.
    Contains business logic and validation rules.
    """
    
    def __init__(
        self,
        user_id: str,
        title: str,
        content: str,
        note_type: NoteType = NoteType.TEXT,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False,
        note_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize note entity.
        
        Args:
            user_id: ID of the user who owns this note
            title: Note title
            content: Note content
            note_type: Type of note
            lesson_id: Associated lesson ID
            section_id: Associated section ID
            tags: List of tags
            is_public: Whether note is public
            note_id: Note ID (auto-generated if not provided)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self._id = note_id or str(uuid.uuid4())
        self._user_id = user_id
        self._title = title
        self._content = content
        self._note_type = note_type
        self._lesson_id = lesson_id
        self._section_id = section_id
        self._tags = tags or []
        self._is_public = is_public
        
        # Statistics
        self._view_count = 0
        self._word_count = len(content.split()) if content else 0
        
        # Timestamps
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate note business rules."""
        if not self._user_id or len(self._user_id.strip()) == 0:
            raise ValueError("User ID cannot be empty")
        
        if not self._title or len(self._title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(self._title) > 200:
            raise ValueError("Title must be no more than 200 characters long")
        
        if not self._content or len(self._content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        if len(self._content) > 50000:
            raise ValueError("Content must be no more than 50000 characters long")
        
        if self._tags and len(self._tags) > 20:
            raise ValueError("Cannot have more than 20 tags")
        
        for tag in self._tags:
            if len(tag) > 50:
                raise ValueError("Tag must be no more than 50 characters long")
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def note_type(self) -> NoteType:
        return self._note_type
    
    @property
    def lesson_id(self) -> Optional[str]:
        return self._lesson_id
    
    @property
    def section_id(self) -> Optional[str]:
        return self._section_id
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    @property
    def is_public(self) -> bool:
        return self._is_public
    
    @property
    def view_count(self) -> int:
        return self._view_count
    
    @property
    def word_count(self) -> int:
        return self._word_count
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Business methods
    def update_title(self, title: str) -> None:
        """
        Update note title.
        
        Args:
            title: New title
            
        Raises:
            ValueError: If title is invalid
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(title) > 200:
            raise ValueError("Title must be no more than 200 characters long")
        
        self._title = title
        self._updated_at = datetime.utcnow()
    
    def update_content(self, content: str) -> None:
        """
        Update note content.
        
        Args:
            content: New content
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or len(content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        if len(content) > 50000:
            raise ValueError("Content must be no more than 50000 characters long")
        
        self._content = content
        self._word_count = len(content.split())
        self._updated_at = datetime.utcnow()
    
    def change_note_type(self, note_type: NoteType) -> None:
        """
        Change note type.
        
        Args:
            note_type: New note type
        """
        self._note_type = note_type
        self._updated_at = datetime.utcnow()
    
    def set_lesson_association(self, lesson_id: Optional[str]) -> None:
        """
        Set lesson association.
        
        Args:
            lesson_id: Lesson ID to associate with
        """
        self._lesson_id = lesson_id
        self._updated_at = datetime.utcnow()
    
    def set_section_association(self, section_id: Optional[str]) -> None:
        """
        Set section association.
        
        Args:
            section_id: Section ID to associate with
        """
        self._section_id = section_id
        self._updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the note.
        
        Args:
            tag: Tag to add
            
        Raises:
            ValueError: If tag is invalid or limit exceeded
        """
        if not tag or len(tag.strip()) == 0:
            raise ValueError("Tag cannot be empty")
        
        if len(tag) > 50:
            raise ValueError("Tag must be no more than 50 characters long")
        
        if len(self._tags) >= 20:
            raise ValueError("Cannot have more than 20 tags")
        
        tag = tag.strip().lower()
        if tag not in self._tags:
            self._tags.append(tag)
            self._updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the note.
        
        Args:
            tag: Tag to remove
        """
        tag = tag.strip().lower()
        if tag in self._tags:
            self._tags.remove(tag)
            self._updated_at = datetime.utcnow()
    
    def set_tags(self, tags: List[str]) -> None:
        """
        Set all tags for the note.
        
        Args:
            tags: List of tags
            
        Raises:
            ValueError: If tags are invalid
        """
        if len(tags) > 20:
            raise ValueError("Cannot have more than 20 tags")
        
        for tag in tags:
            if not tag or len(tag.strip()) == 0:
                raise ValueError("Tag cannot be empty")
            if len(tag) > 50:
                raise ValueError("Tag must be no more than 50 characters long")
        
        self._tags = [tag.strip().lower() for tag in tags]
        self._updated_at = datetime.utcnow()
    
    def toggle_public(self) -> None:
        """Toggle public status."""
        self._is_public = not self._is_public
        self._updated_at = datetime.utcnow()
    
    def set_public(self, is_public: bool) -> None:
        """
        Set public status.
        
        Args:
            is_public: Whether note is public
        """
        self._is_public = is_public
        self._updated_at = datetime.utcnow()
    
    def increment_view_count(self) -> None:
        """Increment view count."""
        self._view_count += 1
        self._updated_at = datetime.utcnow()
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if note has a specific tag.
        
        Args:
            tag: Tag to check
            
        Returns:
            True if note has the tag, False otherwise
        """
        return tag.strip().lower() in self._tags
    
    def get_tags_string(self) -> str:
        """
        Get tags as comma-separated string.
        
        Returns:
            Comma-separated tags string
        """
        return ", ".join(self._tags)
    
    def get_content_preview(self, max_length: int = 200) -> str:
        """
        Get content preview.
        
        Args:
            max_length: Maximum length of preview
            
        Returns:
            Content preview
        """
        if len(self._content) <= max_length:
            return self._content
        
        return self._content[:max_length] + "..."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary representation."""
        return {
            'id': self._id,
            'user_id': self._user_id,
            'title': self._title,
            'content': self._content,
            'note_type': self._note_type.value,
            'lesson_id': self._lesson_id,
            'section_id': self._section_id,
            'tags': self._tags,
            'is_public': self._is_public,
            'view_count': self._view_count,
            'word_count': self._word_count,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"Note({self._title}, {self._note_type.value})"
    
    def __repr__(self) -> str:
        return f"Note(id='{self._id}', title='{self._title}', type='{self._note_type.value}')"
