"""
Web routes for profile management
รองรับการแก้ไขโปรไฟล์และข้อมูลผู้ใช้
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, flash
from functools import wraps
from ..services import UserService
from app import db

# Create blueprint
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@profile_bp.before_request
def load_logged_in_user():
    """Load logged in user for profile routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

# ============================================
# PROFILE WEB ROUTES
# ============================================

@profile_bp.route('/edit')
@login_required_web
def edit_profile():
    """แสดงหน้าแก้ไขโปรไฟล์"""
    return render_template('profile_fragment.html', user=g.user)

@profile_bp.route('/update', methods=['POST'])
@login_required_web
def update_profile():
    """อัปเดตข้อมูลโปรไฟล์ผ่าน web form"""
    try:
        # ตรวจสอบ CSRF token (ถ้าใช้)
        data = request.form
        
        # Validate required fields
        if not data.get('username'):
            flash('กรุณากรอกชื่อผู้ใช้', 'error')
            return redirect(url_for('profile.edit_profile'))
        
        # Initialize user service
        user_service = UserService()
        
        # Update user profile
        updated_user = user_service.update_user_profile(
            user_id=g.user.id,
            first_name=data.get('first_name', '').strip(),
            last_name=data.get('last_name', '').strip(),
            username=data.get('username', '').strip(),
            email=data.get('email', '').strip(),
            bio=data.get('bio', '').strip()
        )
        
        # Update session with new user data
        g.user = updated_user
        
        flash('โปรไฟล์อัปเดตเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('main_routes.dashboard'))
        
    except Exception as e:
        error_message = str(e)
        if 'ชื่อผู้ใช้นี้ถูกใช้แล้ว' in error_message:
            flash('ชื่อผู้ใช้นี้ถูกใช้แล้ว กรุณาเลือกชื่อใหม่', 'error')
        elif 'อีเมลนี้ถูกใช้แล้ว' in error_message:
            flash('อีเมลนี้ถูกใช้แล้ว กรุณาใช้อีเมลอื่น', 'error')
        else:
            flash(f'เกิดข้อผิดพลาดในการอัปเดตโปรไฟล์: {error_message}', 'error')
        
        return redirect(url_for('profile.edit_profile'))

@profile_bp.route('/api/update', methods=['PUT'])
@login_required_web
def api_update_profile():
    """API endpoint สำหรับอัปเดตโปรไฟล์ (AJAX)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'ไม่พบข้อมูลที่ส่งมา'
            }), 400
        
        # Validate required fields
        if not data.get('username'):
            return jsonify({
                'success': False,
                'message': 'กรุณากรอกชื่อผู้ใช้'
            }), 400
        
        # Email validation
        if data.get('email'):
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
                return jsonify({
                    'success': False,
                    'message': 'รูปแบบอีเมลไม่ถูกต้อง'
                }), 400
        
        # Initialize user service
        user_service = UserService()
        
        # Update user profile
        updated_user = user_service.update_user_profile(
            user_id=g.user.id,
            first_name=data.get('first_name', '').strip(),
            last_name=data.get('last_name', '').strip(),
            username=data.get('username', '').strip(),
            email=data.get('email', '').strip(),
            bio=data.get('bio', '').strip()
        )
        
        return jsonify({
            'success': True,
            'message': 'โปรไฟล์อัปเดตเรียบร้อยแล้ว',
            'data': {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'bio': updated_user.bio,
                'profile_image': updated_user.profile_image
            }
        }), 200
        
    except Exception as e:
        error_message = str(e)
        if 'ชื่อผู้ใช้นี้ถูกใช้แล้ว' in error_message:
            return jsonify({
                'success': False,
                'message': 'ชื่อผู้ใช้นี้ถูกใช้แล้ว กรุณาเลือกชื่อใหม่'
            }), 400
        elif 'อีเมลนี้ถูกใช้แล้ว' in error_message:
            return jsonify({
                'success': False,
                'message': 'อีเมลนี้ถูกใช้แล้ว กรุณาใช้อีเมลอื่น'
            }), 400
        else:
            return jsonify({
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการอัปเดตโปรไฟล์: {error_message}'
            }), 500

@profile_bp.route('/view')
@profile_bp.route('/view/<user_id>')
@login_required_web
def view_profile(user_id=None):
    """แสดงโปรไฟล์ของผู้ใช้"""
    try:
        user_service = UserService()
        
        if user_id:
            # View other user's profile
            profile_user = user_service.get_user_by_id(user_id)
        else:
            # View own profile
            profile_user = g.user
        
        if not profile_user:
            flash('ไม่พบผู้ใช้ที่ระบุ', 'error')
            return redirect(url_for('main_routes.dashboard'))
        
        return render_template('profile_view.html', 
                             profile_user=profile_user, 
                             is_own_profile=(profile_user.id == g.user.id))
        
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'error')
        return redirect(url_for('main_routes.dashboard'))