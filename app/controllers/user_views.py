"""
User controller following Clean Architecture principles.
Handles HTTP requests and responses for user operations.
"""

from flask import request, jsonify, session, g
from typing import Dict, Any, Optional
from app.services import UserService
from app.utils.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException
)
from ..middleware import login_required


class UserController:
    """
    Controller for user-related HTTP operations.
    Handles request/response logic and delegates business logic to services.
    """
    
    def __init__(self):
        """Initialize controller with service dependencies."""
        self._user_service = UserService()
    
    def create_user(self) -> Dict[str, Any]:
        """
        Create a new user.
        
        Returns:
            JSON response with created user data
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field} is required'
                    }), 400
            
            # Create user
            user = self._user_service.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=data.get('role', 'student')
            )
            
            return jsonify({
                'success': True,
                'message': 'User created successfully',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }), 201
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 409
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            JSON response with user data
        """
        try:
            user = self._user_service.get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': f'User with ID {user_id} not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_current_user_profile(self) -> Dict[str, Any]:
        """
        Get current user's profile.
        
        Returns:
            JSON response with current user data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            return jsonify({
                'success': True,
                'data': current_user.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def update_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Update user profile.
        
        Args:
            user_id: User ID to update
            
        Returns:
            JSON response with updated user data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            # Check if user can update this profile
            if current_user.id != user_id and not current_user.can_access_admin_features():
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # Prepare update data
            email = None
            if 'email' in data and data['email']:
                email = Email(data['email'])
            
            # Update user
            user = self._user_service.update_user_profile(
                user_id=user_id,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=email
            )
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'data': user.to_dict()
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 409
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def change_password(self, user_id: str) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            
        Returns:
            JSON response
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            # Check if user can change this password
            if current_user.id != user_id and not current_user.can_access_admin_features():
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            required_fields = ['old_password', 'new_password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field} is required'
                    }), 400
            
            # Create new password value object
            new_password = Password(data['new_password'])
            
            # Change password
            self._user_service.change_user_password(
                user_id=user_id,
                old_password=data['old_password'],
                new_password=new_password
            )
            
            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_users(self) -> Dict[str, Any]:
        """
        Get all users with pagination.
        
        Returns:
            JSON response with users list
        """
        try:
            current_user = g.user
            if not current_user or not current_user.can_access_admin_features():
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            # Get pagination parameters
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int)
            
            users = self._user_service.get_all_users(limit=limit, offset=offset)
            
            return jsonify({
                'success': True,
                'data': [user.to_dict() for user in users]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def search_users(self) -> Dict[str, Any]:
        """
        Search users by query.
        
        Returns:
            JSON response with matching users
        """
        try:
            current_user = g.user
            if not current_user or not current_user.can_access_admin_features():
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            query = request.args.get('q', '')
            if not query:
                return jsonify({
                    'success': False,
                    'message': 'Search query is required'
                }), 400
            
            limit = request.args.get('limit', type=int)
            users = self._user_service.search_users(query, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [user.to_dict() for user in users]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            JSON response with user statistics
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            # Check if user can access these statistics
            if current_user.id != user_id and not current_user.can_access_admin_features():
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
            
            statistics = self._user_service.get_user_statistics(user_id)
            
            return jsonify({
                'success': True,
                'data': statistics
            }), 200
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
