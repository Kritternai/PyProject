"""
Register Controller for handling user registration.
Presentation layer implementation.
"""

from flask import request, jsonify, session, redirect, url_for, flash
from ...infrastructure.di.container import get_service
from ...domain.interfaces.services.user_service import UserService
from ...shared.exceptions import ValidationException, BusinessLogicException


class RegisterController:
    """
    Controller for handling user registration operations.
    """
    
    def __init__(self):
        """Initialize the register controller."""
        self._user_service: UserService = get_service(UserService)
    
    def register_user(self):
        """
        Handle user registration.
        
        Returns:
            JSON response with registration result
        """
        try:
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Validate required fields
            if not username or not email or not password:
                return jsonify({
                    'success': False,
                    'message': 'All fields are required.'
                }), 400
            
            # Register user using service
            self._user_service.register_user(username, email, password)
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please log in.',
                'redirect': url_for('auth_web.login')
            })
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred during registration.'
            }), 500
    
    def register_user_web(self):
        """
        Handle user registration for web form.
        
        Returns:
            Redirect response or render template
        """
        try:
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Validate required fields
            if not username or not email or not password:
                flash('All fields are required.', 'danger')
                return redirect(url_for('register.register'))
            
            # Register user using service
            self._user_service.register_user(username, email, password)
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('register.login'))
            
        except ValidationException as e:
            flash(str(e), 'danger')
            return redirect(url_for('register.register'))
            
        except BusinessLogicException as e:
            flash(str(e), 'danger')
            return redirect(url_for('register.register'))
            
        except Exception as e:
            flash('An unexpected error occurred during registration.', 'danger')
            return redirect(url_for('register.register'))
    
    def get_register_form(self):
        """
        Get register form template.
        
        Returns:
            Rendered register form template
        """
        from flask import render_template
        return render_template('register_form.html')
