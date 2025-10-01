"""
User service interface following Service Layer pattern.
Defines contract for user business operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.user import User
from ...value_objects.email import Email
from ...value_objects.password import Password


class UserService(ABC):
    """
    Abstract service interface for User business operations.
    Defines all business logic operations for users.
    """
    
    @abstractmethod
    def create_user(
        self,
        username: str,
        email: Email,
        password: Password,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = 'student'
    ) -> User:
        """
        Create a new user with business validation.
        
        Args:
            username: Unique username
            email: Email value object
            password: Password value object
            first_name: User's first name
            last_name: User's last name
            role: User role
            
        Returns:
            Created user entity
            
        Raises:
            ValidationException: If user data is invalid
            BusinessLogicException: If business rules are violated
        """
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_user_profile(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[Email] = None
    ) -> User:
        """
        Update user profile information.
        
        Args:
            user_id: User ID to update
            first_name: New first name
            last_name: New last name
            email: New email
            
        Returns:
            Updated user entity
            
        Raises:
            NotFoundException: If user doesn't exist
            ValidationException: If data is invalid
        """
        pass
    
    @abstractmethod
    def change_user_password(
        self,
        user_id: str,
        old_password: str,
        new_password: Password
    ) -> None:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Raises:
            NotFoundException: If user doesn't exist
            ValidationException: If old password is incorrect
        """
        pass
    
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User entity if authentication successful, None otherwise
        """
        pass
    
    @abstractmethod
    def verify_user_email(self, user_id: str) -> None:
        """
        Verify user email.
        
        Args:
            user_id: User ID to verify
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    def activate_user(self, user_id: str) -> None:
        """
        Activate user account.
        
        Args:
            user_id: User ID to activate
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    def deactivate_user(self, user_id: str) -> None:
        """
        Deactivate user account.
        
        Args:
            user_id: User ID to deactivate
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user account.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def get_all_users(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            limit: Maximum number of users
            offset: Number of users to skip
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    def search_users(self, query: str, limit: Optional[int] = None) -> List[User]:
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
    def get_users_by_role(self, role: str, limit: Optional[int] = None) -> List[User]:
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
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        pass
    
    @abstractmethod
    def update_user_statistics(
        self,
        user_id: str,
        lesson_count: Optional[int] = None,
        note_count: Optional[int] = None,
        task_count: Optional[int] = None
    ) -> None:
        """
        Update user statistics.
        
        Args:
            user_id: User ID
            lesson_count: New lesson count
            note_count: New note count
            task_count: New task count
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        pass
