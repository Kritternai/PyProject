from app import db
from datetime import datetime
import uuid

class Files(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=True)
    section_id = db.Column(db.String(36), db.ForeignKey('lesson_section.id'), nullable=True)
    note_id = db.Column(db.String(36), db.ForeignKey('note.id'), nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    external_url = db.Column(db.String(500), nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Files('{self.file_name}', '{self.file_path}')" 