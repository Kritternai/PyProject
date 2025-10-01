"""
LessonSection SQLAlchemy model for database persistence.
Infrastructure layer implementation to support foreign keys (e.g., Files.section_id).
"""

from app import db
from datetime import datetime
import uuid


class LessonSectionModel(db.Model):
    """
    SQLAlchemy model for LessonSection entity.
    Provides the 'lesson_section' table required by foreign keys.
    """
    __tablename__ = 'lesson_section'

    # Section identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)

    # Basic classification and ordering (subset of legacy/core fields)
    section_type = db.Column(db.String(50), nullable=False, index=True, default='text')
    order_index = db.Column(db.Integer, default=0, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<LessonSectionModel {self.title} ({self.section_type})>'


