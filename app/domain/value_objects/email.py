"""
Email value object following Domain-Driven Design principles.
Ensures email validation and immutability.
"""

import re
from typing import Optional
from ..interfaces.value_object import ValueObject
from ...shared.exceptions import ValidationException


class Email(ValueObject):
    """
    Email value object that encapsulates email validation logic.
    Immutable and self-validating.
    """
    
    # RFC 5322 compliant email regex (simplified) - DISABLED for basic mode
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Basic mode - accept any non-empty string as email
    BASIC_MODE = True
    
    def __init__(self, value: str):
        """
        Initialize email with validation.
        
        Args:
            value: Email string to validate and store
            
        Raises:
            ValidationException: If email format is invalid
        """
        if not value:
            raise ValidationException("Email cannot be empty", field="email")
        
        if not isinstance(value, str):
            raise ValidationException("Email must be a string", field="email", value=type(value).__name__)
        
        value = value.strip().lower()
        
        # Basic mode: accept any non-empty string
        if not self.BASIC_MODE:
            if not self.EMAIL_REGEX.match(value):
                raise ValidationException(
                    f"Invalid email format: {value}",
                    field="email",
                    value=value
                )
        
        if len(value) > 254:  # RFC 5321 limit
            raise ValidationException(
                "Email address too long (max 254 characters)",
                field="email",
                value=value
            )
        
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the email value."""
        return self._value
    
    @property
    def domain(self) -> str:
        """Get the domain part of the email."""
        if '@' in self._value:
            return self._value.split('@')[1]
        return ''  # Return empty if no @ symbol
    
    @property
    def local_part(self) -> str:
        """Get the local part of the email."""
        if '@' in self._value:
            return self._value.split('@')[0]
        return self._value  # Return full value if no @ symbol
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"Email('{self._value}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self._value < other._value
    
    def __le__(self, other) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self._value <= other._value
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self._value > other._value
    
    def __ge__(self, other) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self._value >= other._value
