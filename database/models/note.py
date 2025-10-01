from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Note(BaseModel):
    """Note model for user notes and annotations"""
    
    # Note identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Note categorization
    note_type = Column(String(50), default='general', index=True)  # general, lesson, section, personal, study
    tags = Column(Text)  # JSON string of tags
    category = Column(String(100))  # study, personal, work, etc.
    
    # Note status and visibility
    status = Column(String(20), default='active', index=True)  # active, archived, deleted
    is_public = Column(Boolean, default=False, index=True)
    is_pinned = Column(Boolean, default=False, index=True)
    
    # Note relationships
    lesson_id = Column(String(36), ForeignKey('lesson.id'), index=True)
    section_id = Column(String(36), ForeignKey('lessonsection.id'), index=True)
    
    # External content
    external_link = Column(String(500))
    source_url = Column(String(500))
    
    # Note metadata
    word_count = Column(String(20))  # estimated word count
    reading_time = Column(String(20))  # estimated reading time
    language = Column(String(10), default='en')  # language code
    
    # Statistics
    view_count = Column(String(20), default=0)
    favorite_count = Column(String(20), default=0)
    
    # Relationships
    user = relationship('User', back_populates='notes')
    lesson = relationship('Lesson', back_populates='notes')
    section = relationship('LessonSection', back_populates='notes')
    files = relationship('Files', back_populates='note', cascade='all, delete-orphan')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_note_user_status', 'user_id', 'status'),
        Index('idx_note_user_type', 'user_id', 'note_type'),
        Index('idx_note_lesson_section', 'lesson_id', 'section_id'),
        Index('idx_note_public_pinned', 'is_public', 'is_pinned'),
    )
    
    @property
    def is_lesson_note(self):
        """Check if note is related to a lesson"""
        return self.lesson_id is not None
    
    @property
    def is_section_note(self):
        """Check if note is related to a lesson section"""
        return self.section_id is not None
    
    @property
    def is_general_note(self):
        """Check if note is a general note"""
        return self.lesson_id is None and self.section_id is None
    
    def __repr__(self):
        return f"<Note '{self.title}' by {self.user_id}>"
