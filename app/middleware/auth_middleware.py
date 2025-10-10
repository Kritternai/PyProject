"""
Authentication middleware for MVC architecture.
"""
from functools import wraps
from flask import request, jsonify, session, g
from typing import Optional
from app.services import UserService
from app.utils.exceptions import AuthenticationException, AuthorizationException


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
        # Check if user is loaded by middleware
        if not hasattr(g, 'user') or not g.user:
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
        
        # User is already loaded by middleware, proceed with the function
        return f(*args, **kwargs)
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
        # Check if user is loaded by middleware
        if not hasattr(g, 'user') or not g.user:
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
        
        # Check if user has admin privileges
        if not g.user.role == 'admin':
            if request.accept_mimetypes['application/json']:
                return jsonify({
                    'success': False,
                    'message': 'Admin privileges required',
                    'error_code': 'ADMIN_REQUIRED'
                }), 403
            else:
                from flask import redirect, url_for, flash
                flash('Admin privileges required.', 'error')
                return redirect(url_for('main_routes.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get current user from g.
    
    Returns:
        Current user or None
    """
    return getattr(g, 'user', None)


def require_user_ownership(user_id: str):
    """
    Decorator to require user ownership of resource.
    
    Args:
        user_id: User ID to check ownership for
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
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
            
            # Check if user owns the resource
            if g.user.id != user_id and g.user.role != 'admin':
                if request.accept_mimetypes['application/json']:
                    return jsonify({
                        'success': False,
                        'message': 'Access denied',
                        'error_code': 'ACCESS_DENIED'
                    }), 403
                else:
                    from flask import redirect, url_for, flash
                    flash('Access denied.', 'error')
                    return redirect(url_for('main_routes.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def load_user():
    """
    Load user into g for easy access.
    This function is called before each request.
    """
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
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
