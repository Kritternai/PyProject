from app import db
from datetime import datetime

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    note_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Note('{self.title}', '{self.note_date}')"