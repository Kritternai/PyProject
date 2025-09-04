from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Integer, Index, Table
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime

class Tag(BaseModel):
    """Tag model for categorizing content"""
    
    # Tag identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Tag appearance
    color = Column(String(7), default='#007bff')  # Hex color code
    icon = Column(String(50))  # FontAwesome icon name
    description = Column(Text)
    
    # Tag categorization
    tag_type = Column(String(20), default='general', index=True)  # general, lesson, note, task, subject, difficulty
    category = Column(String(100))  # study, personal, work, etc.
    
    # Tag usage statistics
    usage_count = Column(Integer, default=0, index=True)
    last_used = Column(DateTime)
    
    # Tag settings
    is_system = Column(String(20), default=False)  # system-generated tags
    is_public = Column(String(20), default=False, index=True)  # public tags for sharing
    is_archived = Column(String(20), default=False, index=True)
    
    # Tag relationships
    user = relationship('User', back_populates='tags')
    lessons = relationship('LessonTag', back_populates='tag', cascade='all, delete-orphan', overlaps="notes")
    notes = relationship('TagRelationship', back_populates='tag', cascade='all, delete-orphan')
    tasks = relationship('TagRelationship', back_populates='tag', cascade='all, delete-orphan')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_tag_user_name', 'user_id', 'name'),
        Index('idx_tag_type_category', 'tag_type', 'category'),
        Index('idx_tag_usage_public', 'usage_count', 'is_public'),
    )
    
    @property
    def display_name(self):
        """Get display name for UI"""
        return self.name.title()
    
    @property
    def is_popular(self):
        """Check if tag is popular (used frequently)"""
        return self.usage_count > 10
    
    def __repr__(self):
        return f'<Tag {self.name} ({self.tag_type})>'


class TagRelationship(BaseModel):
    """Tag relationship model for many-to-many relationships"""
    
    # Relationship identification
    tag_id = Column(String(36), ForeignKey('tag.id'), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    entity_type = Column(String(20), nullable=False, index=True)  # lesson, note, task, section
    
    # Relationship metadata
    relationship_type = Column(String(50), default='tagged')  # tagged, categorized, highlighted
    confidence_score = Column(String(20))  # for AI-generated tags
    
    # Tag relationship
    tag = relationship('Tag', back_populates='notes')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_tag_relationship_entity', 'entity_id', 'entity_type'),
        Index('idx_tag_relationship_tag', 'tag_id', 'entity_type'),
        Index('idx_tag_relationship_type', 'entity_type', 'relationship_type'),
    )
    
    def __repr__(self):
        return f'<TagRelationship {self.tag_id} -> {self.entity_type}:{self.entity_id}>'


# Junction table for lesson tags (many-to-many)
class LessonTag(BaseModel):
    """Lesson tag junction table"""
    
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False, index=True)
    tag_id = Column(String(36), ForeignKey('tag.id'), nullable=False, index=True)
    
    # Relationship metadata
    added_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(String(36), ForeignKey('user.id'), index=True)
    
    # Relationships
    lesson = relationship('Lesson', back_populates='tags')
    tag = relationship('Tag', back_populates='lessons')
    user = relationship('User')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_lesson_tag_lesson', 'lesson_id', 'tag_id'),
        Index('idx_lesson_tag_user', 'added_by'),
    )
    
    def __repr__(self):
        return f'<LessonTag {self.lesson_id} -> {self.tag_id}>'
