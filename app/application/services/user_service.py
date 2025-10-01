"""
User service implementation following Service Layer pattern.
Implements business logic for user operations.
"""

from typing import List, Optional, Dict, Any
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.interfaces.services.user_service import UserService
from app.domain.interfaces.repositories.user_repository import UserRepository
from app.shared.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException
)


class UserServiceImpl(UserService):
    """
    Implementation of UserService interface.
    Contains business logic for user operations.
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize user service with repository dependency.
        
        Args:
            user_repository: User repository implementation
        """
        self._user_repository = user_repository
    
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
        # Business validation
        if self._user_repository.exists_by_username(username):
            raise BusinessLogicException(
                f"Username '{username}' is already taken",
                rule="unique_username"
            )
        
        if self._user_repository.exists_by_email(email):
            raise BusinessLogicException(
                f"Email '{email}' is already registered",
                rule="unique_email"
            )
        
        # Create user entity
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # Save to repository
        return self._user_repository.create(user)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User entity if found, None otherwise
        """
        return self._user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        return self._user_repository.get_by_username(username)
    
    def get_user_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User entity if found, None otherwise
        """
        return self._user_repository.get_by_email(email)
    
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
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        # Check email uniqueness if email is being changed
        if email and email != user.email:
            if self._user_repository.exists_by_email(email):
                raise BusinessLogicException(
                    f"Email '{email}' is already registered",
                    rule="unique_email"
                )
        
        # Update profile
        user.update_profile(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        return self._user_repository.update(user)
    
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
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        try:
            user.change_password(old_password, new_password)
            self._user_repository.update(user)
        except ValueError as e:
            raise ValidationException(str(e), field="old_password")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User entity if authentication successful, None otherwise
        """
        # Try to find user by username first
        user = self._user_repository.get_by_username(username)
        
        # If not found by username, try by email
        if not user:
            try:
                email = Email(username)
                user = self._user_repository.get_by_email(email)
            except ValidationException:
                # Invalid email format, user not found
                return None
        
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # Verify password
        if not user.password.check_password(password):
            return None
        
        # Update last login
        user.update_last_login()
        self._user_repository.update(user)
        
        return user
    
    def verify_user_email(self, user_id: str) -> None:
        """
        Verify user email.
        
        Args:
            user_id: User ID to verify
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        user.verify_email()
        self._user_repository.update(user)
    
    def activate_user(self, user_id: str) -> None:
        """
        Activate user account.
        
        Args:
            user_id: User ID to activate
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        user.activate()
        self._user_repository.update(user)
    
    def deactivate_user(self, user_id: str) -> None:
        """
        Deactivate user account.
        
        Args:
            user_id: User ID to deactivate
            
        Raises:
            NotFoundException: If user doesn't exist
        """
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        user.deactivate()
        self._user_repository.update(user)
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user account.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self._user_repository.delete(user_id)
    
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
        return self._user_repository.get_all(limit=limit, offset=offset)
    
    def search_users(self, query: str, limit: Optional[int] = None) -> List[User]:
        """
        Search users by query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching user entities
        """
        return self._user_repository.search(query, limit=limit)
    
    def get_users_by_role(self, role: str, limit: Optional[int] = None) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
            limit: Maximum number of results
            
        Returns:
            List of user entities with specified role
        """
        return self._user_repository.get_by_role(role, limit=limit)
    
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
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'total_lessons': user.total_lessons,
            'total_notes': user.total_notes,
            'total_tasks': user.total_tasks,
            'is_active': user.is_active,
            'email_verified': user.email_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
    
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
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        # Update statistics (this would need to be implemented in the User entity)
        # For now, we'll just update the user to trigger the updated_at timestamp
        self._user_repository.update(user)
    
    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user (convenience method for create_user).
        
        Args:
            username: Unique username
            email: Email string
            password: Password string
            
        Returns:
            Created user entity
            
        Raises:
            ValidationException: If user data is invalid
            BusinessLogicException: If business rules are violated
        """
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        
        # Convert string parameters to value objects
        email_vo = Email(email)
        password_vo = Password(password)
        
        # Use the existing create_user method
        return self.create_user(username, email_vo, password_vo)
    
    def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user (convenience method).
        
        Args:
            email: Email string
            password: Password string
            
        Returns:
            Authenticated user entity
            
        Raises:
            NotFoundException: If user not found
            ValidationException: If credentials are invalid
        """
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        
        # Convert string parameters to value objects
        email_vo = Email(email)
        password_vo = Password(password)
        
        # Get user by email
        user = self._user_repository.get_by_email(email_vo)
        if not user:
            raise NotFoundException("User", email)
        
        # Verify password
        if not user.password.check_password(password):
            raise ValidationException("Invalid credentials")
        
        return user
