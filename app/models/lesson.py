"""
Lesson SQLAlchemy model for database persistence.
Infrastructure layer implementation.
"""

from app import db
from datetime import datetime
import uuid


class LessonModel(db.Model):
    """
    SQLAlchemy model for Lesson entity.
    Maps domain entity to database table.
    """
    __tablename__ = 'lesson'
    
    # Basic lesson information
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Lesson status and progress
    status = db.Column(db.String(50), default='not_started', nullable=False, index=True)
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Lesson metadata
    difficulty_level = db.Column(db.String(20), default='beginner')
    estimated_duration = db.Column(db.Integer)
    color_theme = db.Column(db.Integer, default=1)
    is_favorite = db.Column(db.Boolean, default=False, index=True)
    
    # External platform integration
    source_platform = db.Column(db.String(50), default='manual', index=True)
    external_id = db.Column(db.String(100), index=True)
    external_url = db.Column(db.String(500))
    
    # Lesson content
    author_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    
    # Statistics
    total_sections = db.Column(db.Integer, default=0)
    completed_sections = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<LessonModel {self.title}>'
    
    def to_dict(self):
        """
        Convert model to dictionary (MVC pattern).
        
        Returns:
            Dictionary representation of lesson
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'difficulty_level': self.difficulty_level,
            'estimated_duration': self.estimated_duration,
            'color_theme': self.color_theme,
            'is_favorite': self.is_favorite,
            'source_platform': self.source_platform,
            'external_id': self.external_id,
            'external_url': self.external_url,
            'author_name': self.author_name,
            'subject': self.subject,
            'grade_level': self.grade_level,
            'total_sections': self.total_sections,
            'completed_sections': self.completed_sections,
            'total_time_spent': self.total_time_spent,
            'cover_image': self.cover_image if hasattr(self, 'cover_image') else None,
            'tags': self.tags if hasattr(self, 'tags') else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
