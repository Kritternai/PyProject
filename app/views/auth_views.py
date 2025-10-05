"""
Authentication views for MVC architecture.
"""
from flask import request, jsonify, session, redirect, url_for, flash, render_template, g
from typing import Dict, Any
from app.services import UserService
from app.utils.exceptions import (
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    BusinessLogicException
)


class AuthController:
    def __init__(self):
        self._user_service = UserService()

    def login(self) -> Any:
        """
        Handles user login.
        Returns:
            JSON response or redirect
        """
        try:
            if request.method == 'GET':
                # Return login form for GET requests
                return render_template('login.html')

            data = request.get_json() if request.is_json else request.form
            if not data:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'message': 'Request body is required'
                    }), 400
                else:
                    flash('Please provide login credentials.', 'error')
                    return redirect(url_for('auth.login'))

            # Validate required fields
            required_fields = ['email', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'message': f'{field} is required'
                        }), 400
                    else:
                        flash(f'{field.title()} is required.', 'error')
                        return redirect(url_for('auth.login'))

            user = self._user_service.authenticate_user(
                email=data['email'],
                password=data['password']
            )

            session['user_id'] = user.id
            session.permanent = True

            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'role': user.role
                        },
                        'redirect_url': url_for('main.dashboard')
                    }
                }), 200
            else:
                flash(f'Welcome back, {user.username}!', 'success')
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
                return redirect(url_for('auth.login'))

        except Exception as e:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Login failed',
                    'error': str(e)
                }), 500
            else:
                flash('Login failed. Please try again.', 'error')
                return redirect(url_for('auth.login'))

    def register(self) -> Any:
        """
        Register a new user.
        Returns:
            JSON response or redirect
        """
        try:
            if request.method == 'GET':
                # Return registration form for GET requests
                return render_template('register.html')

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
            required_fields = ['email', 'password']
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

            # Create user (username will be auto-generated from email)
            username = data.get('username') or data['email'].split('@')[0]
            user = self._user_service.create_user(
                email=data['email'],
                password=data['password'],
                username=username,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=data.get('role', 'student')
            )

            # Don't auto-login after registration - redirect to login page
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful. Please login.',
                    'data': {
                        'redirect_url': url_for('auth.login')
                    }
                }), 201
            else:
                flash(f'Registration successful! Please login with your credentials.', 'success')
                return redirect(url_for('auth.login'))

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
                }), 409 # Conflict
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

    def logout(self) -> Any:
        """
        Logout user.
        Returns:
            Redirect to login page
        """
        session.pop('user_id', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.index'))
