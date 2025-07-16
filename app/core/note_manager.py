from app import db
from datetime import datetime

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Markdown supported
    note_date = db.Column(db.Date, nullable=True)  # วันที่ที่เกี่ยวข้องกับ note
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # เชื่อมกับ User
    user = db.relationship('User', backref='notes')
