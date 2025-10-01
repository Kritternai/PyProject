from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    
    # Basic user information
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # User profile
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # User settings and preferences
    role = db.Column(db.String(20), default='student', nullable=False, index=True)  # student, teacher, admin
    preferences = db.Column(db.Text)  # JSON string for user preferences
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Statistics
    total_lessons = db.Column(db.Integer, default=0)
    total_notes = db.Column(db.Integer, default=0)
    total_tasks = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, email, password, username=None, first_name=None, last_name=None, role='student'):
        self.email = email
        # Auto-generate username from email if not provided
        if username is None:
            username = email.split('@')[0]
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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

    def __repr__(self):
        return f'<User {self.username}>' 