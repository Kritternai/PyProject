from app import db
from datetime import datetime
import uuid

class Note(db.Model):
    __tablename__ = 'note'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=True)
    section_id = db.Column(db.String(36), db.ForeignKey('lesson_section.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Changed from 'body' to 'content'
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    status = db.Column(db.String(20), default='active')
    is_public = db.Column(db.Boolean, default=False)
    external_link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with files
    files = db.relationship('Files', backref='note', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Note('{self.title}', '{self.created_at}')"
