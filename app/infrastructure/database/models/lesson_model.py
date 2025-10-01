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
    
    def to_domain_entity(self):
        """
        Convert SQLAlchemy model to domain entity.
        
        Returns:
            Lesson domain entity
        """
        from app.domain.entities.lesson import Lesson, LessonStatus, DifficultyLevel, SourcePlatform
        
        # Convert string values to enums
        status = LessonStatus(self.status)
        difficulty_level = DifficultyLevel(self.difficulty_level)
        source_platform = SourcePlatform(self.source_platform)
        
        # Create domain entity
        return Lesson(
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            status=status,
            difficulty_level=difficulty_level,
            estimated_duration=self.estimated_duration,
            color_theme=self.color_theme,
            is_favorite=self.is_favorite,
            source_platform=source_platform,
            external_id=self.external_id,
            external_url=self.external_url,
            author_name=self.author_name,
            subject=self.subject,
            grade_level=self.grade_level,
            lesson_id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_domain_entity(cls, lesson):
        """
        Create SQLAlchemy model from domain entity.
        
        Args:
            lesson: Lesson domain entity
            
        Returns:
            LessonModel instance
        """
        return cls(
            id=lesson.id,
            user_id=lesson.user_id,
            title=lesson.title,
            description=lesson.description,
            status=lesson.status.value,
            progress_percentage=lesson.progress_percentage,
            difficulty_level=lesson.difficulty_level.value,
            estimated_duration=lesson.estimated_duration,
            color_theme=lesson.color_theme,
            is_favorite=lesson.is_favorite,
            source_platform=lesson.source_platform.value,
            external_id=lesson.external_id,
            external_url=lesson.external_url,
            author_name=lesson.author_name,
            subject=lesson.subject,
            grade_level=lesson.grade_level,
            total_sections=lesson.total_sections,
            completed_sections=lesson.completed_sections,
            total_time_spent=lesson.total_time_spent,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at
        )
