"""
Web authentication routes for serving HTML pages.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from app.controllers.auth_views import AuthController

# Create web auth blueprint (no url_prefix so routes are at root level)
web_auth_bp = Blueprint('web_auth', __name__)

# Initialize controller
auth_controller = AuthController()

@web_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - serves HTML template and handles form submission"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # Handle form submission
        try:
            result = auth_controller.login()
            # If it's a successful login (redirect or success response)
            if hasattr(result, 'status_code') and result.status_code == 302:
                return result
            elif isinstance(result, dict) and result.get('success'):
                # Successful login - redirect to dashboard silently
                return redirect(url_for('main_routes.dashboard'))
            else:
                # Failed login - stay on login page with error
                flash('อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'error')
                return render_template('login.html')
        except Exception as e:
            flash('เกิดข้อผิดพลาดระหว่างการเข้าสู่ระบบ', 'error')
            return render_template('login.html')

@web_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register page - serves HTML template and handles form submission"""
    if request.method == 'GET':
        return render_template('register.html')
    else:
        # Handle form submission
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate password confirmation
            if not password or not confirm_password:
                flash('กรุณากรอกรหัสผ่านและยืนยันรหัสผ่าน', 'error')
                return render_template('register.html')
                
            if password != confirm_password:
                flash('รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบอีกครั้ง', 'error')
                return render_template('register.html')
                
            # Validate password strength
            if len(password) < 8:
                flash('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร', 'error')
                return render_template('register.html')
            
            result = auth_controller.register()
            
            # If it's a successful registration
            if hasattr(result, 'status_code') and result.status_code == 302:
                return result
            elif isinstance(result, dict) and result.get('success'):
                # Successful registration - redirect to login silently
                return redirect(url_for('web_auth.login'))
            else:
                # Failed registration - AuthController already handled flash messages
                return render_template('register.html')
        except Exception as e:
            # AuthController already handles error messages
            return render_template('register.html')

@web_auth_bp.route('/logout')
def logout():
    """Logout endpoint"""
    try:
        auth_controller.logout()
        return redirect(url_for('web_auth.login'))
    except Exception as e:
        return redirect(url_for('web_auth.login'))

@web_auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page - serves HTML template and handles form submission"""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    else:
        # Handle form submission
        try:
            email = request.form.get('email')
            
            if not email:
                flash('กรุณากรอกอีเมล', 'error')
                return render_template('forgot_password.html')
            
            # TODO: Implement password reset logic
            # For now, just show success message
            flash('หากอีเมลนี้มีอยู่ในระบบ เราจะส่งลิงก์รีเซ็ตรหัสผ่านไปยังอีเมลของคุณ', 'success')
            return render_template('forgot_password.html')
            
        except Exception as e:
            flash('เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง', 'error')
            return render_template('forgot_password.html')

@web_auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password page with token validation"""
    if request.method == 'GET':
        # TODO: Validate token
        return render_template('reset_password.html', token=token)
    else:
        # Handle password reset form submission
        try:
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not password or not confirm_password:
                flash('กรุณากรอกรหัสผ่านและยืนยันรหัสผ่าน', 'error')
                return render_template('reset_password.html', token=token)
                
            if password != confirm_password:
                flash('รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบอีกครั้ง', 'error')
                return render_template('reset_password.html', token=token)
                
            if len(password) < 8:
                flash('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร', 'error')
                return render_template('reset_password.html', token=token)
            
            # TODO: Implement actual password reset logic
            flash('รีเซ็ตรหัสผ่านสำเร็จ กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่', 'success')
            return redirect(url_for('web_auth.login'))
            
        except Exception as e:
            flash('เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง', 'error')
            return render_template('reset_password.html', token=token)