"""
Grade Models - Database models for grade system
Handles grade configuration, categories, items, entries, and summaries
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
import uuid


class GradeConfig(BaseModel):
    """
    Grade configuration for each lesson
    Stores grading scale, passing criteria, and display settings
    """
    __tablename__ = 'grade_config'
    
    lesson_id = Column(String(36), ForeignKey('lesson.id'), unique=True, nullable=False)
    
    # Grading Scale (stored as JSON string)
    # Example: '{"A": {"min": 80, "max": 100, "gpa": 4.0}, ...}'
    grading_scale = Column(Text, nullable=False)
    
    # Configuration
    grading_type = Column(String(20), default='percentage')  # percentage, points, letter
    total_points = Column(Numeric(10, 2), default=100)
    passing_grade = Column(String(5), default='D')
    passing_percentage = Column(Numeric(5, 2), default=50.0)
    
    # Display settings
    show_total_grade = Column(Boolean, default=True)
    allow_what_if = Column(Boolean, default=True)
    show_class_average = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<GradeConfig lesson_id={self.lesson_id}>'


class GradeCategory(BaseModel):
    """
    Grade categories for organizing assignments
    Examples: Assignments, Quizzes, Midterm, Final
    """
    __tablename__ = 'grade_category'
    
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Weight & Points
    weight = Column(Numeric(5, 2), nullable=False)  # Percentage weight (0-100)
    total_points = Column(Numeric(10, 2))
    
    # Drop rules
    drop_lowest = Column(Integer, default=0)
    drop_highest = Column(Integer, default=0)
    
    # Display
    color = Column(String(7), default='#3B82F6')
    icon = Column(String(50), default='bi-clipboard')
    order_index = Column(Integer, default=0)
    
    def __repr__(self):
        return f'<GradeCategory {self.name} weight={self.weight}%>'


class GradeItem(BaseModel):
    """
    Individual grade items (assignments, quizzes, exams)
    """
    __tablename__ = 'grade_item'
    
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False)
    category_id = Column(String(36), ForeignKey('grade_category.id'), nullable=False)
    
    # Item info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Points
    points_possible = Column(Numeric(10, 2), nullable=False)
    
    # Dates
    due_date = Column(DateTime)
    published_date = Column(DateTime)
    
    # Settings
    is_published = Column(Boolean, default=False)
    is_extra_credit = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<GradeItem {self.name} ({self.points_possible} pts)>'


class GradeEntry(BaseModel):
    """
    Student grade entries for each grade item
    """
    __tablename__ = 'grade_entry'
    
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False)
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False)
    grade_item_id = Column(String(36), ForeignKey('grade_item.id'), nullable=False)
    
    # Score
    score = Column(Numeric(10, 2))
    points_possible = Column(Numeric(10, 2))  # Snapshot at time of grading
    
    # Status
    status = Column(String(20), default='pending')  # pending, graded, excused, missing
    is_excused = Column(Boolean, default=False)
    
    # Feedback
    comments = Column(Text)
    graded_by = Column(String(36), ForeignKey('user.id'))
    graded_at = Column(DateTime)
    
    # Late submission
    is_late = Column(Boolean, default=False)
    late_penalty = Column(Numeric(5, 2), default=0)
    
    def __repr__(self):
        return f'<GradeEntry user={self.user_id} item={self.grade_item_id} score={self.score}>'
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.points_possible and self.points_possible > 0:
            return round((float(self.score or 0) / float(self.points_possible)) * 100, 2)
        return 0


class GradeSummary(BaseModel):
    """
    Cached grade summary for each student in each lesson
    Improves performance by pre-calculating totals
    """
    __tablename__ = 'grade_summary'
    
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False)
    lesson_id = Column(String(36), ForeignKey('lesson.id'), nullable=False)
    
    # Current grade
    current_score = Column(Numeric(10, 2))
    total_possible = Column(Numeric(10, 2))
    percentage = Column(Numeric(5, 2))
    letter_grade = Column(String(5))
    gpa = Column(Numeric(3, 2))
    
    # Status
    is_passing = Column(Boolean, default=True)
    
    # What-if calculations (stored as JSON string)
    points_to_pass = Column(Numeric(10, 2))
    points_to_next_grade = Column(Text)  # JSON: {"A": 8.5, "B+": 5.0}
    
    # Metadata
    last_calculated = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='uix_user_lesson_grade'),
    )
    
    def __repr__(self):
        return f'<GradeSummary user={self.user_id} lesson={self.lesson_id} grade={self.letter_grade}>'

