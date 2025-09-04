"""
Exception module for the application.
Provides all custom exception classes.
"""

from .base_exception import (
    BaseApplicationException,
    ValidationException,
    NotFoundException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ExternalServiceException
)

__all__ = [
    'BaseApplicationException',
    'ValidationException',
    'NotFoundException',
    'AuthenticationException',
    'AuthorizationException',
    'BusinessLogicException',
    'ExternalServiceException'
]
