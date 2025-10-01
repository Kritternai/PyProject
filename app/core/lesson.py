from app import db
import uuid
from datetime import datetime

class Lesson(db.Model):
    __tablename__ = 'lesson'
    
    # Basic lesson information
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Lesson status and progress
    status = db.Column(db.String(50), default='not_started', nullable=False, index=True)  # not_started, in_progress, completed, archived
    progress_percentage = db.Column(db.Integer, default=0)  # 0-100
    
    # Lesson metadata
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    estimated_duration = db.Column(db.Integer)  # minutes
    color_theme = db.Column(db.Integer, default=1)  # 1-6 color themes
    is_favorite = db.Column(db.Boolean, default=False, index=True)
    
    # External platform integration
    source_platform = db.Column(db.String(50), default='manual', index=True)  # manual, google_classroom, ms_teams, canvas
    external_id = db.Column(db.String(100), index=True)  # ID from external platform
    external_url = db.Column(db.String(500))  # URL to external platform
    
    # Lesson content
    author_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    
    # Statistics
    total_sections = db.Column(db.Integer, default=0)
    completed_sections = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)  # minutes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sections = db.relationship('LessonSection', backref='lesson', lazy=True, order_by='LessonSection.order_index')
    notes = db.relationship('Note', backref='lesson', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('Files', backref='lesson', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Lesson {self.title}>'

    @property
    def note_count(self):
        """Count notes associated with this lesson"""
        return len(self.notes)

    @property
    def file_count(self):
        """Count files associated with this lesson"""
        return len(self.files)

    @property
    def is_completed(self):
        """Check if lesson is completed"""
        return self.status == 'completed'
    
    @property
    def progress_ratio(self):
        """Get progress as ratio (0.0 to 1.0)"""
        return self.progress_percentage / 100.0

    @property
    def manual_assignment_count(self):
        """Count sections of type 'assignment' for manually created lessons"""
        if self.source_platform == 'manual':
            return len([s for s in self.sections if s.section_type == 'assignment'])
        return 0

class LessonSection(db.Model):
    __tablename__ = 'lesson_section'
    
    # Section identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    
    # Section type and organization
    section_type = db.Column(db.String(50), nullable=False, index=True)  # text, file, assignment, note, material, quiz, video
    order_index = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(50), default='pending', index=True)  # pending, in_progress, completed, skipped
    
    # Section metadata
    tags = db.Column(db.Text)  # JSON string of tags
    due_date = db.Column(db.DateTime)
    estimated_duration = db.Column(db.Integer)  # minutes
    points = db.Column(db.Integer, default=0)  # points for assignments/quizzes
    
    # Progress tracking
    time_spent = db.Column(db.Integer, default=0)  # minutes
    completion_percentage = db.Column(db.Integer, default=0)  # 0-100
    
    # External content
    external_url = db.Column(db.String(500))
    external_id = db.Column(db.String(100))
    
    # Legacy fields for backward compatibility
    type = db.Column(db.String(20), default='text')  # text, file, assignment, note
    file_urls = db.Column(db.Text, nullable=True)  # JSON array of file urls
    assignment_due = db.Column(db.DateTime, nullable=True)
    order = db.Column(db.Integer, default=0)  # Legacy order field
    body = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    files = db.relationship('Files', backref='section', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LessonSection {self.title} ({self.section_type})>'
    
    @property
    def order(self):
        """Backward compatibility for order field"""
        return self.order_index
