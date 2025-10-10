"""
Grade Models - SQLAlchemy models for grade system
Following MVC pattern: Models handle data persistence
"""

from app import db
from datetime import datetime
import uuid
import json


class GradeConfig(db.Model):
    """
    Grade configuration for each lesson
    Stores grading scale, passing criteria, and display settings
    """
    __tablename__ = 'grade_config'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), unique=True, nullable=False)
    
    # Grading Scale (stored as JSON string)
    grading_scale = db.Column(db.Text, nullable=False)
    
    # Configuration
    grading_type = db.Column(db.String(20), default='percentage')
    total_points = db.Column(db.Numeric(10, 2), default=100)
    passing_grade = db.Column(db.String(5), default='D')
    passing_percentage = db.Column(db.Numeric(5, 2), default=50.0)
    
    # Display settings
    show_total_grade = db.Column(db.Boolean, default=True)
    allow_what_if = db.Column(db.Boolean, default=True)
    show_class_average = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GradeConfig lesson_id={self.lesson_id}>'


class GradeCategory(db.Model):
    """
    Grade categories for organizing assignments
    Examples: Assignments, Quizzes, Midterm, Final
    """
    __tablename__ = 'grade_category'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Weight & Points
    weight = db.Column(db.Numeric(5, 2), nullable=False)
    total_points = db.Column(db.Numeric(10, 2))
    
    # Drop rules
    drop_lowest = db.Column(db.Integer, default=0)
    drop_highest = db.Column(db.Integer, default=0)
    
    # Display
    color = db.Column(db.String(7), default='#3B82F6')
    icon = db.Column(db.String(50), default='bi-clipboard')
    order_index = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GradeCategory {self.name} weight={self.weight}%>'


class GradeItem(db.Model):
    """
    Individual grade items (assignments, quizzes, exams)
    """
    __tablename__ = 'grade_item'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('grade_category.id'), nullable=False)
    
    # Item info
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Points
    points_possible = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Dates
    due_date = db.Column(db.DateTime)
    published_date = db.Column(db.DateTime)
    
    # Settings
    is_published = db.Column(db.Boolean, default=False)
    is_extra_credit = db.Column(db.Boolean, default=False)
    is_muted = db.Column(db.Boolean, default=False)
    
    # Link to Classwork Task
    classwork_task_id = db.Column(db.String(36), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GradeItem {self.name} ({self.points_possible} pts)>'


class GradeEntry(db.Model):
    """
    Student grade entries for each grade item
    """
    __tablename__ = 'grade_entry'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False)
    grade_item_id = db.Column(db.String(36), db.ForeignKey('grade_item.id'), nullable=False)
    
    # Score
    score = db.Column(db.Numeric(10, 2))
    points_possible = db.Column(db.Numeric(10, 2))
    
    # Status
    status = db.Column(db.String(20), default='pending')
    is_excused = db.Column(db.Boolean, default=False)
    
    # Feedback
    comments = db.Column(db.Text)
    graded_by = db.Column(db.String(36), db.ForeignKey('user.id'))
    graded_at = db.Column(db.DateTime)
    
    # Late submission
    is_late = db.Column(db.Boolean, default=False)
    late_penalty = db.Column(db.Numeric(5, 2), default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GradeEntry user={self.user_id} item={self.grade_item_id} score={self.score}>'
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.points_possible and self.points_possible > 0:
            return round((float(self.score or 0) / float(self.points_possible)) * 100, 2)
        return 0


class GradeSummary(db.Model):
    """
    Cached grade summary for each student in each lesson
    """
    __tablename__ = 'grade_summary'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False)
    
    # Current grade
    current_score = db.Column(db.Numeric(10, 2))
    total_possible = db.Column(db.Numeric(10, 2))
    percentage = db.Column(db.Numeric(5, 2))
    letter_grade = db.Column(db.String(5))
    gpa = db.Column(db.Numeric(3, 2))
    
    # Status
    is_passing = db.Column(db.Boolean, default=True)
    
    # What-if calculations
    points_to_pass = db.Column(db.Numeric(10, 2))
    points_to_next_grade = db.Column(db.Text)  # JSON string
    
    # Metadata
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='uix_user_lesson_grade'),
    )
    
    def __repr__(self):
        return f'<GradeSummary user={self.user_id} lesson={self.lesson_id} grade={self.letter_grade}>'

