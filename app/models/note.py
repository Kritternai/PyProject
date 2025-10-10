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
    # Legacy/extended fields for UI features
    status = db.Column(db.String(50))  # pending, in-progress, completed
    external_link = db.Column(db.String(500))
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<NoteModel {self.title}>'
    
    def to_dict(self):
        """
        Convert model to dictionary (MVC pattern).
        
        Returns:
            Dictionary representation of note
        """
        # Parse tags from JSON
        tags = []
        if self.tags:
            try:
                tags = json.loads(self.tags) if isinstance(self.tags, str) else self.tags
            except (json.JSONDecodeError, TypeError):
                tags = []
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'note_type': self.note_type,
            'lesson_id': self.lesson_id,
            'section_id': self.section_id,
            'tags': tags,
            'is_public': self.is_public,
            'status': self.status,
            'external_link': self.external_link,
            'view_count': self.view_count,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
