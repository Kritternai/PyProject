from app import db
import uuid
import datetime

class CourseLinkage(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    kmitl_course_identifier = db.Column(db.String(255), nullable=False, unique=True) # e.g., "67030011_2568_1_03206111"
    google_classroom_id = db.Column(db.String(255), nullable=False)
    linked_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<CourseLinkage {self.kmitl_course_identifier} -> {self.google_classroom_id}>'
