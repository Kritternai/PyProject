"""
User SQLAlchemy model for database persistence.
Infrastructure layer implementation.
"""

from app import db
from datetime import datetime
import uuid


class UserModel(db.Model):
    """
    SQLAlchemy model for User entity.
    Maps domain entity to database table.
    """
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
    role = db.Column(db.String(20), default='student', nullable=False, index=True)
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
    
    def __repr__(self):
        return f'<UserModel {self.username}>'
    
    def to_dict(self):
        """
        Convert model to dictionary (MVC pattern).
        
        Returns:
            Dictionary representation of user
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image': self.profile_image,
            'bio': self.bio,
            'role': self.role,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_lessons': self.total_lessons,
            'total_notes': self.total_notes,
            'total_tasks': self.total_tasks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
