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
            
            # Prepare update data - handle email validation
            email_str = None
            if 'email' in data and data['email']:
                email_str = data['email']
                # Basic email validation
                import re
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_str):
                    return jsonify({
                        'success': False,
                        'message': 'รูปแบบอีเมลไม่ถูกต้อง'
                    }), 400
            
            # Update user
            user = self._user_service.update_user_profile(
                user_id=user_id,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                username=data.get('username'),
                email=email_str,
                bio=data.get('bio'),
                profile_image=data.get('profile_image')
            )
            
            return jsonify({
                'success': True,
                'message': 'โปรไฟล์อัปเดตเรียบร้อยแล้ว',
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

    def update_current_user_profile(self) -> Dict[str, Any]:
        """
        Update current user's profile.
        
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
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # Use user service to update profile
            updated_user = self._user_service.update_user_profile(
                user_id=current_user.id,
                first_name=data.get('first_name', '').strip(),
                last_name=data.get('last_name', '').strip(),
                username=data.get('username', '').strip(),
                email=data.get('email', '').strip(),
                bio=data.get('bio', '').strip()
            )
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'data': {
                    'id': updated_user.id,
                    'username': updated_user.username,
                    'email': updated_user.email,
                    'first_name': updated_user.first_name,
                    'last_name': updated_user.last_name,
                    'bio': updated_user.bio,
                    'profile_image': updated_user.profile_image,
                    'role': updated_user.role,
                    'email_verified': updated_user.email_verified
                }
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 400
            
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 409
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500

    def export_current_user_data(self) -> Dict[str, Any]:
        """
        Export current user's data as JSON.
        
        Returns:
            JSON response with user data for download
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            # Collect user data
            user_data = {
                'profile': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'email': current_user.email,
                    'first_name': current_user.first_name,
                    'last_name': current_user.last_name,
                    'bio': current_user.bio,
                    'role': current_user.role,
                    'email_verified': current_user.email_verified,
                    'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
                    'updated_at': current_user.updated_at.isoformat() if current_user.updated_at else None,
                    'last_login': current_user.last_login.isoformat() if current_user.last_login else None
                },
                'statistics': {
                    'total_lessons': current_user.total_lessons or 0,
                    'total_notes': current_user.total_notes or 0,
                    'total_tasks': current_user.total_tasks or 0
                },
                'privacy_note': {
                    'oauth_user': current_user.password_hash == 'oauth_google',
                    'note': 'This data export contains only internal system data. No real personal information from Google OAuth is stored.'
                }
            }
            
            from flask import make_response
            import json
            
            # Create response with proper headers for download
            response = make_response(json.dumps(user_data, indent=2, ensure_ascii=False))
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{current_user.username}.json'
            
            return response
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
