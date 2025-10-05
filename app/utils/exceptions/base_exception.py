"""
Base exception classes for the application.
Following Clean Architecture principles.
"""

from abc import ABC
from typing import Optional, Dict, Any


class BaseApplicationException(Exception, ABC):
    """
    Base exception class for all application exceptions.
    Provides common structure for error handling.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class ValidationException(BaseApplicationException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = value
        
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details=details
        )


class NotFoundException(BaseApplicationException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            error_code='NOT_FOUND',
            details={'resource_type': resource_type, 'resource_id': resource_id}
        )


class AuthenticationException(BaseApplicationException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code='AUTHENTICATION_ERROR'
        )


class AuthorizationException(BaseApplicationException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code='AUTHORIZATION_ERROR'
        )


class BusinessLogicException(BaseApplicationException):
    """Raised when business logic rules are violated."""
    
    def __init__(self, message: str, rule: Optional[str] = None):
        details = {}
        if rule:
            details['rule'] = rule
        
        super().__init__(
            message=message,
            error_code='BUSINESS_LOGIC_ERROR',
            details=details
        )


class ExternalServiceException(BaseApplicationException):
    """Raised when external service calls fail."""
    
    def __init__(self, service_name: str, message: str, status_code: Optional[int] = None):
        details = {'service_name': service_name}
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            error_code='EXTERNAL_SERVICE_ERROR',
            details=details
        )
