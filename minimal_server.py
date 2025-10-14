#!/usr/bin/env python3
"""
Minimal Flask Server
เซิร์ฟเวอร์ Flask แบบง่ายสำหรับทดสอบ Profile system
"""

from flask import Flask, render_template, session, g, redirect, url_for, jsonify
import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create minimal Flask app
app = Flask(__name__)
app.secret_key = 'test-secret-key-for-profile-system'

# Mock user data for testing
MOCK_USER = {
    'id': 'test-user-123',
    'username': 'testuser',
    'email': 'testuser@internal.system',
    'first_name': 'Test',
    'last_name': 'User',
    'bio': 'This is a test user for profile system',
    'role': 'student',
    'email_verified': True,
    'is_active': True,
    'password_hash': 'oauth_google',
    'profile_image': None,
    'total_lessons': 5,
    'total_notes': 12,
    'total_tasks': 3,
    'created_at': '2025-10-14',
    'updated_at': '2025-10-14',
    'last_login': '2025-10-14'
}

@app.before_request
def load_user():
    """Load mock user for testing"""
    g.user = type('User', (), MOCK_USER)()

@app.route('/')
def index():
    """Homepage - login or redirect to dashboard"""
    session['user_id'] = 'test-user-123'  # Auto-login for testing
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile System Test</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center mb-4">🧪 Profile System Test</h1>
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">ระบบ Profile พร้อมใช้งาน!</h5>
                            <p class="card-text">ทดสอบระบบ Profile ที่สร้างขึ้น</p>
                            <a href="/profile-view" class="btn btn-primary">
                                <i class="bi bi-person-circle me-2"></i>ดูโปรไฟล์
                            </a>
                            <a href="/profile-edit" class="btn btn-outline-primary">
                                <i class="bi bi-pencil me-2"></i>แก้ไขโปรไฟล์
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/profile-view')
def profile_view():
    """Profile view page"""
    try:
        return render_template('profile_view.html', 
                             profile_user=g.user,
                             is_own_profile=True)
    except Exception as e:
        return f'''
        <div class="container mt-5">
            <div class="alert alert-warning">
                <h4>Template Error</h4>
                <p>ไม่สามารถโหลด profile_view.html: {e}</p>
                <p><strong>Template path:</strong> app/templates/profile_view.html</p>
                <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
            </div>
        </div>
        '''

@app.route('/profile-edit')
def profile_edit():
    """Profile edit page"""
    try:
        return render_template('profile_fragment.html', user=g.user)
    except Exception as e:
        return f'''
        <div class="container mt-5">
            <div class="alert alert-warning">
                <h4>Template Error</h4>
                <p>ไม่สามารถโหลด profile_fragment.html: {e}</p>
                <p><strong>Template path:</strong> app/templates/profile_fragment.html</p>
                <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
            </div>
        </div>
        '''

@app.route('/api/users/current/profile', methods=['PUT'])
def update_profile():
    """Mock API for profile update"""
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully (mock)',
        'data': MOCK_USER
    })

@app.route('/api/users/current/export')
def export_user_data():
    """Mock API for data export"""
    import json
    from flask import make_response
    
    export_data = {
        'profile': MOCK_USER,
        'export_date': '2025-10-14',
        'note': 'This is test data for profile system'
    }
    
    response = make_response(json.dumps(export_data, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=test_user_data.json'
    return response

if __name__ == '__main__':
    print("🚀 Starting Minimal Flask Server for Profile Testing")
    print("=" * 60)
    print("📍 Homepage: http://localhost:5003")
    print("👤 Profile View: http://localhost:5003/profile-view")
    print("✏️ Profile Edit: http://localhost:5003/profile-edit")
    print("⏹️ Stop: Ctrl+C")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5003, debug=True)