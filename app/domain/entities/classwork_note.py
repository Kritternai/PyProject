"""
Classwork Note Entity
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class ClassworkNote:
    """Classwork Note Entity"""
    
    id: str
    user_id: str
    lesson_id: str
    title: str
    content: Optional[str] = None
    subject: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    task_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []
    
    def get_content_length(self) -> int:
        """Get content length"""
        return len(self.content) if self.content else 0
    
    def get_word_count(self) -> int:
        """Get word count of content"""
        if not self.content:
            return 0
        return len(self.content.split())
    
    def is_empty(self) -> bool:
        """Check if note is empty"""
        return not self.content or self.content.strip() == ""
    
    def add_tag(self, tag: str):
        """Add a tag to the note"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the note"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def update_content(self, new_content: str):
        """Update note content"""
        self.content = new_content
        self.updated_at = datetime.now()
    
    def get_preview(self, max_length: int = 100) -> str:
        """Get content preview"""
        if not self.content:
            return ""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'content': self.content,
            'subject': self.subject,
            'category': self.category,
            'tags': self.tags,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'content_length': self.get_content_length(),
            'word_count': self.get_word_count(),
            'is_empty': self.is_empty(),
            'preview': self.get_preview()
        }
