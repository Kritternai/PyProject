"""
User repository interface following Repository pattern.
Defines contract for user data access operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.user import User
from ...value_objects.email import Email


class UserRepository(ABC):
    """
    Abstract repository interface for User entity.
    Defines all data access operations for users.
    """
    
    @abstractmethod
    def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user entity
            
        Raises:
            ValidationException: If user data is invalid
        """
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email value object to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """
        Update existing user.
        
        Args:
            user: User entity to update
            
        Returns:
            Updated user entity
            
        Raises:
            NotFoundException: If user doesn't exist
            ValidationException: If user data is invalid
        """
        pass
    
    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """
        Check if user exists by username.
        
        Args:
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    def search(self, query: str, limit: Optional[int] = None) -> List[User]:
        """
        Search users by query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching user entities
        """
        pass
    
    @abstractmethod
    def get_by_role(self, role: str, limit: Optional[int] = None) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
            limit: Maximum number of results
            
        Returns:
            List of user entities with specified role
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Total count of users
        """
        pass
    
    @abstractmethod
    def get_active_users(self, limit: Optional[int] = None) -> List[User]:
        """
        Get all active users.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of active user entities
        """
        pass
