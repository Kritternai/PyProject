"""
Dashboard Controller for handling dashboard operations.
Presentation layer implementation.
"""

from flask import g, render_template, redirect, url_for, flash
from functools import wraps
from ...infrastructure.di.container import get_service
from ...domain.interfaces.services.user_service import UserService


class DashboardController:
    """
    Controller for handling dashboard operations.
    """
    
    def __init__(self):
        """Initialize the dashboard controller."""
        self._user_service: UserService = get_service(UserService)
    
    def login_required_web(self, f):
        """
        Decorator to require login for web routes.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('register.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def load_logged_in_user(self):
        """
        Load logged in user for web routes.
        """
        from flask import session
        user_id = session.get('user_id')
        if user_id:
            try:
                g.user = self._user_service.get_user_by_id(user_id)
            except:
                g.user = None
        else:
            g.user = None
    
    def get_dashboard(self):
        """
        Get dashboard page.
        
        Returns:
            Rendered dashboard template
        """
        if not g.user:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('register.login'))
        
        return render_template('dashboard.html', user=g.user)
    
    def get_dashboard_data(self):
        """
        Get dashboard data for AJAX.
        
        Returns:
            JSON response with dashboard data
        """
        if not g.user:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            # Get user data
            user_data = {
                'id': str(g.user.id),
                'username': g.user.username,
                'email': g.user.email,
                'created_at': g.user.created_at.isoformat() if g.user.created_at else None
            }
            
            return jsonify({
                'success': True,
                'data': user_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
