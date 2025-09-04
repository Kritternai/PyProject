"""
Password value object following Domain-Driven Design principles.
Handles password validation and hashing.
"""

import re
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from ..interfaces.value_object import ValueObject
from ...shared.exceptions import ValidationException


class Password(ValueObject):
    """
    Password value object that encapsulates password validation and hashing.
    Immutable and self-validating.
    """
    
    # Password requirements
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Special characters allowed
    SPECIAL_CHARS = r'!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    def __init__(self, value: str, is_hashed: bool = False):
        """
        Initialize password with validation.
        
        Args:
            value: Password string to validate and store
            is_hashed: Whether the password is already hashed
            
        Raises:
            ValidationException: If password doesn't meet requirements
        """
        if not value:
            raise ValidationException("Password cannot be empty", field="password")
        
        if not isinstance(value, str):
            raise ValidationException("Password must be a string", field="password", value=type(value).__name__)
        
        if is_hashed:
            # For hashed passwords, just store them
            self._value = value
            self._is_hashed = True
        else:
            # Validate plain text password
            self._validate_password(value)
            self._value = generate_password_hash(value)
            self._is_hashed = True
    
    def _validate_password(self, password: str) -> None:
        """
        Validate password against requirements.
        
        Args:
            password: Plain text password to validate
            
        Raises:
            ValidationException: If password doesn't meet requirements
        """
        if len(password) < self.MIN_LENGTH:
            raise ValidationException(
                f"Password must be at least {self.MIN_LENGTH} characters long",
                field="password"
            )
        
        if len(password) > self.MAX_LENGTH:
            raise ValidationException(
                f"Password must be no more than {self.MAX_LENGTH} characters long",
                field="password"
            )
        
        if self.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            raise ValidationException(
                "Password must contain at least one uppercase letter",
                field="password"
            )
        
        if self.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            raise ValidationException(
                "Password must contain at least one lowercase letter",
                field="password"
            )
        
        if self.REQUIRE_DIGITS and not re.search(r'\d', password):
            raise ValidationException(
                "Password must contain at least one digit",
                field="password"
            )
        
        if self.REQUIRE_SPECIAL_CHARS and not re.search(f'[{re.escape(self.SPECIAL_CHARS)}]', password):
            raise ValidationException(
                f"Password must contain at least one special character ({self.SPECIAL_CHARS})",
                field="password"
            )
    
    def check_password(self, plain_password: str) -> bool:
        """
        Check if plain password matches the hashed password.
        
        Args:
            plain_password: Plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        if not self._is_hashed:
            return False
        
        return check_password_hash(self._value, plain_password)
    
    @property
    def value(self) -> str:
        """Get the hashed password value."""
        return self._value
    
    @property
    def is_hashed(self) -> bool:
        """Check if password is hashed."""
        return self._is_hashed
    
    def __str__(self) -> str:
        return "***"  # Never expose password in string representation
    
    def __repr__(self) -> str:
        return "Password(***)"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Password):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
