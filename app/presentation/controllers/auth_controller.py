"""
Authentication controller following Clean Architecture principles.
Handles authentication-related HTTP operations.
"""

from flask import request, jsonify, session, redirect, url_for, flash
from typing import Dict, Any
from ...domain.interfaces.services.user_service import UserService
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...shared.exceptions import (
    ValidationException,
    AuthenticationException,
    BusinessLogicException
)
from ...infrastructure.di.container import get_service


class AuthController:
    """
    Controller for authentication-related HTTP operations.
    Handles login, logout, and registration.
    """
    
    def __init__(self):
        """Initialize controller with service dependencies."""
        self._user_service: UserService = get_service(UserService)
    
    def login(self) -> Dict[str, Any]:
        """
        Authenticate user and create session.
        
        Returns:
            JSON response or redirect
        """
        try:
            if request.method == 'GET':
                # Return login form for GET requests
                return redirect(url_for('auth.login_page'))
            
            data = request.get_json() if request.is_json else request.form
            if not data:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Request body is required'
                    }), 400
                else:
                    flash('Please provide login credentials.', 'error')
                    return redirect(url_for('auth.login_page'))
            
            # Validate required fields
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Username and password are required'
                    }), 400
                else:
                    flash('Username and password are required.', 'error')
                    return redirect(url_for('auth.login_page'))
            
            # Authenticate user
            user = self._user_service.authenticate_user(username, password)
            if not user:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid username or password',
                        'error_code': 'INVALID_CREDENTIALS'
                    }), 401
                else:
                    flash('Invalid username or password.', 'error')
                    return redirect(url_for('auth.login_page'))
            
            # Create session
            session['user_id'] = user.id
            session.permanent = True
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        'user': user.to_dict(),
                        'redirect_url': url_for('main.dashboard')
                    }
                }), 200
            else:
                flash(f'Welcome back, {user.display_name}!', 'success')
                return redirect(url_for('main.dashboard'))
                
        except ValidationException as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': e.message,
                    'error_code': e.error_code,
                    'details': e.details
                }), 400
            else:
                flash(e.message, 'error')
                return redirect(url_for('auth.login_page'))
                
        except Exception as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Login failed',
                    'error': str(e)
                }), 500
            else:
                flash('Login failed. Please try again.', 'error')
                return redirect(url_for('auth.login_page'))
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout user and clear session.
        
        Returns:
            JSON response or redirect
        """
        try:
            # Clear session
            session.clear()
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Logout successful',
                    'redirect_url': url_for('main.index')
                }), 200
            else:
                flash('You have been logged out successfully.', 'info')
                return redirect(url_for('main.index'))
                
        except Exception as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Logout failed',
                    'error': str(e)
                }), 500
            else:
                flash('Logout failed.', 'error')
                return redirect(url_for('main.index'))
    
    def register(self) -> Dict[str, Any]:
        """
        Register a new user.
        
        Returns:
            JSON response or redirect
        """
        try:
            if request.method == 'GET':
                # Return registration form for GET requests
                return redirect(url_for('auth.register'))
            
            data = request.get_json() if request.is_json else request.form
            if not data:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Request body is required'
                    }), 400
                else:
                    flash('Please provide registration information.', 'error')
                    return redirect(url_for('auth.register'))
            
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'message': f'{field} is required'
                        }), 400
                    else:
                        flash(f'{field.title()} is required.', 'error')
                        return redirect(url_for('auth.register'))
            
            # Validate password confirmation
            if 'confirm_password' in data and data['password'] != data['confirm_password']:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Passwords do not match'
                    }), 400
                else:
                    flash('Passwords do not match.', 'error')
                    return redirect(url_for('auth.register'))
            
            # Create value objects
            email = Email(data['email'])
            password = Password(data['password'])
            
            # Create user
            user = self._user_service.create_user(
                username=data['username'],
                email=email,
                password=password,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=data.get('role', 'student')
            )
            
            # Auto-login after registration
            session['user_id'] = user.id
            session.permanent = True
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful',
                    'data': {
                        'user': user.to_dict(),
                        'redirect_url': url_for('main.dashboard')
                    }
                }), 201
            else:
                flash(f'Welcome, {user.display_name}! Your account has been created.', 'success')
                return redirect(url_for('main.dashboard'))
                
        except ValidationException as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': e.message,
                    'error_code': e.error_code,
                    'details': e.details
                }), 400
            else:
                flash(e.message, 'error')
                return redirect(url_for('auth.register'))
                
        except BusinessLogicException as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': e.message,
                    'error_code': e.error_code,
                    'details': e.details
                }), 409
            else:
                flash(e.message, 'error')
                return redirect(url_for('auth.register'))
                
        except Exception as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Registration failed',
                    'error': str(e)
                }), 500
            else:
                flash('Registration failed. Please try again.', 'error')
                return redirect(url_for('auth.register'))
    
    def check_auth_status(self) -> Dict[str, Any]:
        """
        Check current authentication status.
        
        Returns:
            JSON response with auth status
        """
        try:
            from ..middleware.auth_middleware import get_current_user
            current_user = get_current_user()
            
            if current_user:
                return jsonify({
                    'success': True,
                    'authenticated': True,
                    'user': current_user.to_dict()
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'authenticated': False,
                    'user': None
                }), 200
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Failed to check authentication status',
                'error': str(e)
            }), 500
