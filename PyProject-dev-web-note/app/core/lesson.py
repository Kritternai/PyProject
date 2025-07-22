from app import db
import uuid

class Lesson(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Not Started') # e.g., Not Started, In Progress, Completed
    tags = db.Column(db.String(200), nullable=True) # Comma-separated tags
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Lesson {self.title}>'
