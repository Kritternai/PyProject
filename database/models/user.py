from sqlalchemy import Column, String, Boolean, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    """User model for authentication and user management"""
    
    # Basic user information
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    
    # User profile
    first_name = Column(String(50))
    last_name = Column(String(50))
    profile_image = Column(String(255))
    bio = Column(Text)
    
    # User settings and preferences
    role = Column(String(20), default='student', nullable=False, index=True)  # student, teacher, admin
    preferences = Column(Text)  # JSON string for user preferences
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime)
    
    # Statistics
    total_lessons = Column(Integer, default=0)
    total_notes = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    
    # Relationships
    lessons = relationship('Lesson', back_populates='user', cascade='all, delete-orphan')
    notes = relationship('Note', back_populates='user', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='user', cascade='all, delete-orphan')
    files = relationship('Files', back_populates='user', cascade='all, delete-orphan')
    tags = relationship('Tag', back_populates='user', cascade='all, delete-orphan')
    integrations = relationship('ExternalIntegration', back_populates='user', cascade='all, delete-orphan')
    progress_records = relationship('ProgressTracking', back_populates='user', cascade='all, delete-orphan', foreign_keys='ProgressTracking.user_id')
    pomodoro_sessions = relationship('PomodoroSession', back_populates='user', cascade='all, delete-orphan')
    reminders = relationship('Reminder', back_populates='user', cascade='all, delete-orphan')
    reports = relationship('Report', back_populates='user', cascade='all, delete-orphan')
    activity_logs = relationship('ActivityLog', back_populates='user', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def display_name(self):
        """Get display name for UI"""
        return self.full_name or self.username
    
    def set_password(self, password):
        """Set user password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check user password"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
