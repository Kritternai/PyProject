"""
User repository implementation using SQLAlchemy.
Infrastructure layer implementation of UserRepository interface.
"""

from typing import List, Optional
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.interfaces.repositories.user_repository import UserRepository
from ..models.user_model import UserModel
from app import db
from app.shared.exceptions import ValidationException


class UserRepositoryImpl(UserRepository):
    """
    SQLAlchemy implementation of UserRepository interface.
    Handles all database operations for User entity.
    """
    
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
        try:
            user_model = UserModel.from_domain_entity(user)
            db.session.add(user_model)
            db.session.commit()
            return user_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to create user: {str(e)}")
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User entity if found, None otherwise
        """
        user_model = UserModel.query.filter_by(id=user_id).first()
        return user_model.to_domain_entity() if user_model else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User entity if found, None otherwise
        """
        user_model = UserModel.query.filter_by(username=username).first()
        return user_model.to_domain_entity() if user_model else None
    
    def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email value object to search for
            
        Returns:
            User entity if found, None otherwise
        """
        user_model = UserModel.query.filter_by(email=str(email)).first()
        return user_model.to_domain_entity() if user_model else None
    
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
        try:
            user_model = UserModel.query.filter_by(id=user.id).first()
            if not user_model:
                from ...shared.exceptions import NotFoundException
                raise NotFoundException("User", user.id)
            
            # Update fields
            user_model.username = user.username
            user_model.email = str(user.email)
            user_model.password_hash = user.password.value
            user_model.first_name = user.first_name
            user_model.last_name = user.last_name
            user_model.role = user.role
            user_model.is_active = user.is_active
            user_model.email_verified = user.email_verified
            user_model.last_login = user.last_login
            user_model.total_lessons = user.total_lessons
            user_model.total_notes = user.total_notes
            user_model.total_tasks = user.total_tasks
            user_model.updated_at = user.updated_at
            
            db.session.commit()
            return user_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            if "NotFoundException" in str(type(e)):
                raise
            raise ValidationException(f"Failed to update user: {str(e)}")
    
    def delete(self, user_id: str) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            user_model = UserModel.query.filter_by(id=user_id).first()
            if not user_model:
                return False
            
            db.session.delete(user_model)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to delete user: {str(e)}")
    
    def exists_by_username(self, username: str) -> bool:
        """
        Check if user exists by username.
        
        Args:
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        return UserModel.query.filter_by(username=username).first() is not None
    
    def exists_by_email(self, email: Email) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        return UserModel.query.filter_by(email=str(email)).first() is not None
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of user entities
        """
        query = UserModel.query.order_by(UserModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        user_models = query.all()
        return [user_model.to_domain_entity() for user_model in user_models]
    
    def search(self, query: str, limit: Optional[int] = None) -> List[User]:
        """
        Search users by query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching user entities
        """
        search_query = UserModel.query.filter(
            db.or_(
                UserModel.username.contains(query),
                UserModel.first_name.contains(query),
                UserModel.last_name.contains(query),
                UserModel.email.contains(query)
            )
        ).order_by(UserModel.username)
        
        if limit:
            search_query = search_query.limit(limit)
        
        user_models = search_query.all()
        return [user_model.to_domain_entity() for user_model in user_models]
    
    def get_by_role(self, role: str, limit: Optional[int] = None) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
            limit: Maximum number of results
            
        Returns:
            List of user entities with specified role
        """
        query = UserModel.query.filter_by(role=role).order_by(UserModel.username)
        
        if limit:
            query = query.limit(limit)
        
        user_models = query.all()
        return [user_model.to_domain_entity() for user_model in user_models]
    
    def count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Total count of users
        """
        return UserModel.query.count()
    
    def get_active_users(self, limit: Optional[int] = None) -> List[User]:
        """
        Get all active users.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of active user entities
        """
        query = UserModel.query.filter_by(is_active=True).order_by(UserModel.username)
        
        if limit:
            query = query.limit(limit)
        
        user_models = query.all()
        return [user_model.to_domain_entity() for user_model in user_models]
