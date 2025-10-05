"""
Classwork Material Entity
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MaterialType(Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"

@dataclass
class ClassworkMaterial:
    """Classwork Material Entity"""
    
    id: str
    user_id: str
    lesson_id: str
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[MaterialType] = None
    file_size: Optional[int] = None
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
    
    def get_file_extension(self) -> str:
        """Get file extension from file_path"""
        if not self.file_path:
            return ""
        return self.file_path.split('.')[-1].lower()
    
    def get_file_size_mb(self) -> float:
        """Get file size in MB"""
        if self.file_size is None:
            return 0.0
        return self.file_size / (1024 * 1024)
    
    def is_image(self) -> bool:
        """Check if material is an image"""
        if not self.file_type:
            return False
        return self.file_type == MaterialType.IMAGE
    
    def is_document(self) -> bool:
        """Check if material is a document"""
        if not self.file_type:
            return False
        return self.file_type == MaterialType.DOCUMENT
    
    def is_video(self) -> bool:
        """Check if material is a video"""
        if not self.file_type:
            return False
        return self.file_type == MaterialType.VIDEO
    
    def add_tag(self, tag: str):
        """Add a tag to the material"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the material"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type.value if self.file_type else None,
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'subject': self.subject,
            'category': self.category,
            'tags': self.tags,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'file_extension': self.get_file_extension(),
            'is_image': self.is_image(),
            'is_document': self.is_document(),
            'is_video': self.is_video()
        }
