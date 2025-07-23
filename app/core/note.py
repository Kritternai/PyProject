from app import db
from datetime import datetime
import uuid

class Note(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) # Use UUID for ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    external_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='notes')

    def __repr__(self):
        return f'<Note {self.title}>'
