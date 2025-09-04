"""
Authentication middleware following Clean Architecture principles.
Handles authentication and authorization logic.
"""

from functools import wraps
from flask import request, jsonify, session, g
from typing import Optional
from app.domain.interfaces.services.user_service import UserService
from app.shared.exceptions import AuthenticationException, AuthorizationException
from app.infrastructure.di.container import get_service


def login_required(f):
    """
    Decorator to require user authentication.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required',
                    'error_code': 'AUTHENTICATION_REQUIRED'
                }), 401
            else:
                from flask import redirect, url_for, flash
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        # Load user into g for easy access
        try:
            user_service: UserService = get_service(UserService)
            user = user_service.get_user_by_id(user_id)
            if not user or not user.is_active:
                session.pop('user_id', None)
                if request.accept_mimetypes['application/json']:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid or inactive user',
                        'error_code': 'INVALID_USER'
                    }), 401
                else:
                    from flask import redirect, url_for, flash
                    flash('Your account is inactive. Please contact support.', 'error')
                    return redirect(url_for('auth.login'))
            
            g.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            session.pop('user_id', None)
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Authentication error',
                    'error_code': 'AUTHENTICATION_ERROR'
                }), 401
            else:
                from flask import redirect, url_for, flash
                flash('Authentication error. Please log in again.', 'error')
                return redirect(url_for('auth.login'))
    
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required',
                    'error_code': 'AUTHENTICATION_REQUIRED'
                }), 401
            else:
                from flask import redirect, url_for, flash
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        try:
            user_service: UserService = get_service(UserService)
            user = user_service.get_user_by_id(user_id)
            if not user or not user.can_access_admin_features():
                if request.accept_mimetypes['application/json']:
                    return jsonify({
                        'success': False,
                        'message': 'Admin privileges required',
                        'error_code': 'ADMIN_REQUIRED'
                    }), 403
                else:
                    from flask import redirect, url_for, flash
                    flash('You do not have permission to access this page.', 'error')
                    return redirect(url_for('main.dashboard'))
            
            g.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Authorization error',
                    'error_code': 'AUTHORIZATION_ERROR'
                }), 403
            else:
                from flask import redirect, url_for, flash
                flash('Authorization error.', 'error')
                return redirect(url_for('main.dashboard'))
    
    return decorated_function


def teacher_required(f):
    """
    Decorator to require teacher or admin privileges.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required',
                    'error_code': 'AUTHENTICATION_REQUIRED'
                }), 401
            else:
                from flask import redirect, url_for, flash
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        try:
            user_service: UserService = get_service(UserService)
            user = user_service.get_user_by_id(user_id)
            if not user or not user.can_manage_lessons():
                if request.accept_mimetypes['application/json']:
                    return jsonify({
                        'success': False,
                        'message': 'Teacher or admin privileges required',
                        'error_code': 'TEACHER_REQUIRED'
                    }), 403
                else:
                    from flask import redirect, url_for, flash
                    flash('You do not have permission to access this page.', 'error')
                    return redirect(url_for('main.dashboard'))
            
            g.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Authorization error',
                    'error_code': 'AUTHORIZATION_ERROR'
                }), 403
            else:
                from flask import redirect, url_for, flash
                flash('Authorization error.', 'error')
                return redirect(url_for('main.dashboard'))
    
    return decorated_function


def get_current_user():
    """
    Get the current authenticated user.
    
    Returns:
        Current user entity or None if not authenticated
    """
    return getattr(g, 'user', None)


def require_user_ownership(user_id: str):
    """
    Decorator to require that the current user owns the resource or is admin.
    
    Args:
        user_id: User ID to check ownership for
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                if request.accept_mimetypes['application/json']:
                    return jsonify({
                        'success': False,
                        'message': 'Authentication required',
                        'error_code': 'AUTHENTICATION_REQUIRED'
                    }), 401
                else:
                    from flask import redirect, url_for, flash
                    flash('Please log in to access this page.', 'warning')
                    return redirect(url_for('auth.login'))
            
            if current_user.id != user_id and not current_user.can_access_admin_features():
                if request.accept_mimetypes['application/json']:
                    return jsonify({
                        'success': False,
                        'message': 'Access denied',
                        'error_code': 'ACCESS_DENIED'
                    }), 403
                else:
                    from flask import redirect, url_for, flash
                    flash('You do not have permission to access this resource.', 'error')
                    return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def load_user():
    """
    Load user into g context for all requests.
    This should be called in before_request.
    """
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service: UserService = get_service(UserService)
            user = user_service.get_user_by_id(user_id)
            if user and user.is_active:
                g.user = user
            else:
                g.user = None
                session.pop('user_id', None)
        except Exception:
            g.user = None
            session.pop('user_id', None)
    else:
        g.user = None
