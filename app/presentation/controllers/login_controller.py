"""
Login Controller for handling user authentication.
Presentation layer implementation.
"""

from flask import request, jsonify, session, redirect, url_for, flash
from ...infrastructure.di.container import get_service
from ...domain.interfaces.services.user_service import UserService
from ...shared.exceptions import ValidationException, NotFoundException


class LoginController:
    """
    Controller for handling user authentication operations.
    """
    
    def __init__(self):
        """Initialize the login controller."""
        self._user_service: UserService = get_service(UserService)
    
    def authenticate_user(self):
        """
        Handle user authentication.
        
        Returns:
            JSON response with authentication result
        """
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Validate required fields
            if not email or not password:
                return jsonify({
                    'success': False,
                    'message': 'Email and password are required.'
                }), 400
            
            # Authenticate user using service
            user = self._user_service.authenticate_user(email, password)
            
            # Set session
            session['user_id'] = str(user.id)
            
            return jsonify({
                'success': True,
                'message': 'Logged in successfully!',
                'redirect': url_for('auth_web.dashboard')
            })
            
        except (NotFoundException, ValidationException) as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 401
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred during login.'
            }), 500
    
    def authenticate_user_web(self):
        """
        Handle user authentication for web form.
        
        Returns:
            Redirect response or render template
        """
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Validate required fields
            if not email or not password:
                flash('Email and password are required.', 'danger')
                return redirect(url_for('register.login'))
            
            # Authenticate user using service
            user = self._user_service.authenticate_user(email, password)
            
            # Set session
            session['user_id'] = str(user.id)
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('register.dashboard'))
            
        except (NotFoundException, ValidationException) as e:
            flash(str(e), 'danger')
            return redirect(url_for('register.login'))
            
        except Exception as e:
            # Log the actual error for debugging
            import traceback
            print(f"Login error: {str(e)}")
            print(traceback.format_exc())
            flash(f'Login error: {str(e)}', 'danger')
            return redirect(url_for('register.login'))
    
    def get_login_form(self):
        """
        Get login form template.
        
        Returns:
            Rendered login form template
        """
        from flask import render_template
        return render_template('login_form.html')
    
    def logout_user(self):
        """
        Handle user logout.
        
        Returns:
            Redirect response
        """
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('register.login'))
