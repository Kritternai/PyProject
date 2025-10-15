"""
Authentication middleware for MVC architecture.
"""
from functools import wraps
from flask import request, jsonify, session, g
from typing import Optional
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
            # Import directly from the main services.py file to avoid circular imports
            import importlib.util
            import os
            
            # Get the path to the main services.py file
            services_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services.py')
            
            # Load the services module directly
            spec = importlib.util.spec_from_file_location("app_services", services_path)
            app_services = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app_services)
            
            # Get UserService from the loaded module
            UserService = app_services.UserService
            
            user_service = UserService()
            user = user_service.get_user_by_id(user_id)
            if user and user.is_active:
                g.user = user
            else:
                g.user = None
                session.pop('user_id', None)
        except ImportError as ie:
            print(f"Import error loading UserService: {str(ie)}")
            g.user = None
            session.pop('user_id', None)
        except Exception as e:
            print(f"Error loading user: {str(e)}")
            g.user = None
            session.pop('user_id', None)
    else:
        g.user = None
