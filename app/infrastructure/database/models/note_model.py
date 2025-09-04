"""
Note SQLAlchemy model for database persistence.
Infrastructure layer implementation.
"""

from app import db
from datetime import datetime
import uuid
import json


class NoteModel(db.Model):
    """
    SQLAlchemy model for Note entity.
    Maps domain entity to database table.
    """
    __tablename__ = 'note'
    
    # Basic note information
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(20), default='text', nullable=False, index=True)
    
    # Associations
    lesson_id = db.Column(db.String(36), nullable=True, index=True)
    section_id = db.Column(db.String(36), nullable=True, index=True)
    
    # Metadata
    tags = db.Column(db.Text)  # JSON string of tags
    is_public = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<NoteModel {self.title}>'
    
    def to_domain_entity(self):
        """
        Convert SQLAlchemy model to domain entity.
        
        Returns:
            Note domain entity
        """
        from app.domain.entities.note import Note, NoteType
        
        # Parse tags from JSON
        tags = []
        if self.tags:
            try:
                tags = json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                tags = []
        
        # Convert string to enum
        note_type = NoteType(self.note_type)
        
        # Create domain entity
        return Note(
            user_id=self.user_id,
            title=self.title,
            content=self.content,
            note_type=note_type,
            lesson_id=self.lesson_id,
            section_id=self.section_id,
            tags=tags,
            is_public=self.is_public,
            note_id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_domain_entity(cls, note):
        """
        Create SQLAlchemy model from domain entity.
        
        Args:
            note: Note domain entity
            
        Returns:
            NoteModel instance
        """
        return cls(
            id=note.id,
            user_id=note.user_id,
            title=note.title,
            content=note.content,
            note_type=note.note_type.value,
            lesson_id=note.lesson_id,
            section_id=note.section_id,
            tags=json.dumps(note.tags) if note.tags else None,
            is_public=note.is_public,
            view_count=note.view_count,
            word_count=note.word_count,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
