from app import db
import uuid

class Lesson(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Not Started') # e.g., Not Started, In Progress, Completed
    tags = db.Column(db.String(200), nullable=True) # Comma-separated tags
    author_name = db.Column(db.String(100), nullable=True) # New field for lesson author
    selected_color = db.Column(db.Integer, default=1) # Color theme for lesson card (1-6)
    is_favorite = db.Column(db.Boolean, default=False) # Favorite/starred lesson
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    google_classroom_id = db.Column(db.String(100), nullable=True) # New field for Google Classroom Course ID
    source_platform = db.Column(db.String(50), default='manual') # e.g., 'manual', 'google_classroom'
    classroom_assignments_count = db.Column(db.Integer, default=0) # Count of Google Classroom assignments
    announcements_data = db.Column(db.Text, nullable=True)
    topics_data = db.Column(db.Text, nullable=True)
    roster_data = db.Column(db.Text, nullable=True)
    attachments_data = db.Column(db.Text, nullable=True)
    sections = db.relationship('LessonSection', backref='lesson', lazy=True, order_by='LessonSection.order')
    
    # Relationships with Notes and Files
    notes = db.relationship('Note', backref='lesson', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('Files', backref='lesson', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Lesson {self.title}>'

    @property
    def note_count(self):
        # Count notes associated with this lesson
        return len(self.notes)

    @property
    def file_count(self):
        # Count files associated with this lesson
        return len(self.files)

    @property
    def manual_assignment_count(self):
        # Count sections of type 'assignment' for manually created lessons
        # Google Classroom assignments are handled by classroom_assignments_count
        if self.source_platform == 'manual':
            return len([s for s in self.sections if s.type == 'assignment'])
        return 0

class LessonSection(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), default='text') # text, file, assignment, note
    file_urls = db.Column(db.Text, nullable=True) # JSON array of file urls (for multiple files)
    assignment_due = db.Column(db.DateTime, nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    # Fields for note type
    body = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    external_link = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(50), default='pending')
    
    # Relationships with Files
    files = db.relationship('Files', backref='section', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LessonSection {self.title} ({self.type})>'
