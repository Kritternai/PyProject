"""
User domain entity following Domain-Driven Design principles.
Pure business object with no external dependencies.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from ..value_objects.email import Email
from ..value_objects.password import Password
from ..interfaces.entity import Entity


class User(Entity):
    """
    User domain entity representing a user in the system.
    Contains business logic and validation rules.
    """
    
    def __init__(
        self,
        username: str,
        email: Email,
        password: Password,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = 'student',
        user_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize user entity.
        
        Args:
            username: Unique username
            email: Email value object
            password: Password value object
            first_name: User's first name
            last_name: User's last name
            role: User role (student, teacher, admin)
            user_id: User ID (auto-generated if not provided)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self._id = user_id or str(uuid.uuid4())
        self._username = username
        self._email = email
        self._password = password
        self._first_name = first_name
        self._last_name = last_name
        self._role = role
        self._is_active = True
        self._email_verified = False
        self._last_login = None
        self._total_lessons = 0
        self._total_notes = 0
        self._total_tasks = 0
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate user business rules."""
        if not self._username or len(self._username.strip()) == 0:
            raise ValueError("Username cannot be empty")
        
        if len(self._username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if len(self._username) > 50:
            raise ValueError("Username must be no more than 50 characters long")
        
        if not self._username.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        
        if self._first_name and len(self._first_name) > 50:
            raise ValueError("First name must be no more than 50 characters long")
        
        if self._last_name and len(self._last_name) > 50:
            raise ValueError("Last name must be no more than 50 characters long")
        
        if self._role not in ['student', 'teacher', 'admin']:
            raise ValueError("Role must be one of: student, teacher, admin")
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> Email:
        return self._email
    
    @property
    def password(self) -> Password:
        return self._password
    
    @property
    def first_name(self) -> Optional[str]:
        return self._first_name
    
    @property
    def last_name(self) -> Optional[str]:
        return self._last_name
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def email_verified(self) -> bool:
        return self._email_verified
    
    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login
    
    @property
    def total_lessons(self) -> int:
        return self._total_lessons
    
    @property
    def total_notes(self) -> int:
        return self._total_notes
    
    @property
    def total_tasks(self) -> int:
        return self._total_tasks
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Business methods
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self._first_name and self._last_name:
            return f"{self._first_name} {self._last_name}"
        return self._username
    
    @property
    def display_name(self) -> str:
        """Get display name for UI."""
        return self.full_name
    
    def change_password(self, old_password: str, new_password: Password) -> None:
        """
        Change user password.
        
        Args:
            old_password: Current password for verification
            new_password: New password value object
            
        Raises:
            ValueError: If old password is incorrect
        """
        if not self._password.check_password(old_password):
            raise ValueError("Current password is incorrect")
        
        self._password = new_password
        self._updated_at = datetime.utcnow()
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self._email_verified = True
        self._updated_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self._last_login = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account."""
        self._is_active = True
        self._updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self._is_active = False
        self._updated_at = datetime.utcnow()
    
    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[Email] = None
    ) -> None:
        """
        Update user profile information.
        
        Args:
            first_name: New first name
            last_name: New last name
            email: New email
        """
        if first_name is not None:
            if len(first_name) > 50:
                raise ValueError("First name must be no more than 50 characters long")
            self._first_name = first_name
        
        if last_name is not None:
            if len(last_name) > 50:
                raise ValueError("Last name must be no more than 50 characters long")
            self._last_name = last_name
        
        if email is not None:
            self._email = email
            self._email_verified = False  # Reset verification when email changes
        
        self._updated_at = datetime.utcnow()
    
    def increment_lesson_count(self) -> None:
        """Increment total lessons count."""
        self._total_lessons += 1
        self._updated_at = datetime.utcnow()
    
    def increment_note_count(self) -> None:
        """Increment total notes count."""
        self._total_notes += 1
        self._updated_at = datetime.utcnow()
    
    def increment_task_count(self) -> None:
        """Increment total tasks count."""
        self._total_tasks += 1
        self._updated_at = datetime.utcnow()
    
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self._role == 'admin'
    
    def is_teacher(self) -> bool:
        """Check if user is teacher."""
        return self._role == 'teacher'
    
    def is_student(self) -> bool:
        """Check if user is student."""
        return self._role == 'student'
    
    def can_access_admin_features(self) -> bool:
        """Check if user can access admin features."""
        return self.is_admin() and self._is_active
    
    def can_manage_lessons(self) -> bool:
        """Check if user can manage lessons."""
        return self.is_teacher() or self.is_admin()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            'id': self._id,
            'username': self._username,
            'email': str(self._email),
            'first_name': self._first_name,
            'last_name': self._last_name,
            'role': self._role,
            'is_active': self._is_active,
            'email_verified': self._email_verified,
            'last_login': self._last_login.isoformat() if self._last_login else None,
            'total_lessons': self._total_lessons,
            'total_notes': self._total_notes,
            'total_tasks': self._total_tasks,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"User({self._username}, {self._email})"
    
    def __repr__(self) -> str:
        return f"User(id='{self._id}', username='{self._username}', email='{self._email}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
