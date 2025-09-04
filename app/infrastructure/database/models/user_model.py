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
    
    def to_domain_entity(self):
        """
        Convert SQLAlchemy model to domain entity.
        
        Returns:
            User domain entity
        """
        from app.domain.entities.user import User
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        
        # Create value objects
        email = Email(self.email)
        password = Password(self.password_hash, is_hashed=True)
        
        # Create domain entity
        return User(
            username=self.username,
            email=email,
            password=password,
            first_name=self.first_name,
            last_name=self.last_name,
            role=self.role,
            user_id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_domain_entity(cls, user):
        """
        Create SQLAlchemy model from domain entity.
        
        Args:
            user: User domain entity
            
        Returns:
            UserModel instance
        """
        return cls(
            id=user.id,
            username=user.username,
            email=str(user.email),
            password_hash=user.password.value,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            email_verified=user.email_verified,
            last_login=user.last_login,
            total_lessons=user.total_lessons,
            total_notes=user.total_notes,
            total_tasks=user.total_tasks,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
