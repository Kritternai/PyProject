#!/usr/bin/env python3
"""
Simple Profile Test Server
เซิร์ฟเวอร์ทดสอบระบบ Profile แบบง่าย ๆ
"""

from flask import Flask, render_template, request, session, g, jsonify, redirect, url_for
import sqlite3
import os
from pathlib import Path

# Simple Flask app
app = Flask(__name__)
app.secret_key = 'test_secret_key_for_profile'

# Database path
DB_PATH = Path(__file__).parent / 'instance' / 'site.db'

def get_db():
    """Get database connection"""
    try:
        db = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row  # Enable named access to columns
        return db
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_sample_user():
    """Get sample user for testing"""
    return {
        'id': 1,
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'ทดสอบ',
        'last_name': 'ระบบ',
        'display_name': 'ทดสอบ ระบบ',
        'profile_image': None,
        'bio': 'ผู้ใช้ทดสอบระบบ Profile',
        'created_at': '2024-01-01',
        'email_verified': True,
        'privacy_google_oauth': False
    }

@app.before_request
def load_logged_in_user():
    """Load user for testing"""
    # For testing, always use sample user
    g.user = get_sample_user()
    session['user_id'] = 1

@app.route('/')
def index():
    """หน้าหลัก"""
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Profile Test Server</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .card { box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: none; border-radius: 15px; }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body text-center p-5">
                            <h1 class="display-4 mb-4">🧪 Profile Test Server</h1>
                            <p class="lead">ทดสอบระบบ Profile ที่เราสร้างไว้</p>
                            
                            <div class="row mt-4">
                                <div class="col-md-6">
                                    <a href="/profile/view" class="btn btn-primary btn-lg w-100 mb-3">
                                        <i class="bi bi-person-circle me-2"></i>Profile View
                                    </a>
                                </div>
                                <div class="col-md-6">
                                    <a href="/profile/edit" class="btn btn-success btn-lg w-100 mb-3">
                                        <i class="bi bi-pencil me-2"></i>Profile Edit
                                    </a>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <a href="/test/templates" class="btn btn-warning btn-lg w-100 mb-3">
                                        <i class="bi bi-file-earmark-text me-2"></i>Test Templates
                                    </a>
                                </div>
                                <div class="col-md-6">
                                    <a href="/test/api" class="btn btn-info btn-lg w-100 mb-3">
                                        <i class="bi bi-gear me-2"></i>Test API
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/profile/view')
def profile_view():
    """หน้าแสดง Profile"""
    try:
        # ลองใช้ template ที่เราสร้างไว้
        template_path = Path(__file__).parent / 'app' / 'templates' / 'profile_view.html'
        if template_path.exists():
            return render_template('profile_view.html', user=g.user)
        else:
            return f"""
            <div class="alert alert-warning">
                <h4>⚠️ Template ไม่พบ</h4>
                <p>ไฟล์ <code>profile_view.html</code> ไม่พบที่: {template_path}</p>
                <p>ผู้ใช้ทดสอบ: {g.user}</p>
                <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
            </div>
            """
    except Exception as e:
        return f"""
        <div class="alert alert-danger">
            <h4>❌ Error loading profile view</h4>
            <p>Error: {str(e)}</p>
            <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
        </div>
        """

@app.route('/profile/edit')
def profile_edit():
    """หน้าแก้ไข Profile"""
    try:
        # ลองใช้ template ที่เราสร้างไว้
        template_path = Path(__file__).parent / 'app' / 'templates' / 'profile_fragment.html'
        if template_path.exists():
            return render_template('profile_fragment.html', user=g.user)
        else:
            return f"""
            <div class="alert alert-warning">
                <h4>⚠️ Template ไม่พบ</h4>
                <p>ไฟล์ <code>profile_fragment.html</code> ไม่พบที่: {template_path}</p>
                <p>ผู้ใช้ทดสอบ: {g.user}</p>
                <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
            </div>
            """
    except Exception as e:
        return f"""
        <div class="alert alert-danger">
            <h4>❌ Error loading profile edit</h4>
            <p>Error: {str(e)}</p>
            <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
        </div>
        """

@app.route('/test/templates')
def test_templates():
    """ทดสอบ Templates"""
    templates_dir = Path(__file__).parent / 'app' / 'templates'
    template_files = []
    
    if templates_dir.exists():
        for file in templates_dir.glob('*profile*.html'):
            template_files.append({
                'name': file.name,
                'path': str(file),
                'exists': file.exists(),
                'size': file.stat().st_size if file.exists() else 0
            })
    
    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>Template Test</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>📄 Template Status</h1>
            <div class="row">
                <div class="col-md-12">
                    <h3>Template Directory: {templates_dir}</h3>
                    <p>Directory exists: <span class="badge bg-{'success' if templates_dir.exists() else 'danger'}">{'Yes' if templates_dir.exists() else 'No'}</span></p>
                    
                    <h4>Profile Templates:</h4>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Template</th>
                                    <th>Path</th>
                                    <th>Exists</th>
                                    <th>Size</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    for template in template_files:
        status_badge = 'success' if template['exists'] else 'danger'
        status_text = 'Yes' if template['exists'] else 'No'
        html += f"""
                                <tr>
                                    <td><code>{template['name']}</code></td>
                                    <td><small>{template['path']}</small></td>
                                    <td><span class="badge bg-{status_badge}">{status_text}</span></td>
                                    <td>{template['size']} bytes</td>
                                </tr>
        """
    
    html += """
                            </tbody>
                        </table>
                    </div>
                    <a href="/" class="btn btn-primary">กลับหน้าหลัก</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/test/api')
def test_api():
    """ทดสอบ API"""
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>API Test</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>🔧 API Test</h1>
            <div class="row">
                <div class="col-md-12">
                    <h3>Available API Endpoints:</h3>
                    <ul class="list-group">
                        <li class="list-group-item">
                            <strong>GET /api/profile/current</strong> - Get current user profile
                        </li>
                        <li class="list-group-item">
                            <strong>PUT /api/profile/current</strong> - Update current user profile
                        </li>
                        <li class="list-group-item">
                            <strong>GET /api/profile/export</strong> - Export user data
                        </li>
                    </ul>
                    
                    <div class="mt-4">
                        <h4>Quick Test:</h4>
                        <button class="btn btn-primary" onclick="testAPI()">Test Current Profile API</button>
                        <div id="api-result" class="mt-3"></div>
                    </div>
                    
                    <a href="/" class="btn btn-secondary mt-3">กลับหน้าหลัก</a>
                </div>
            </div>
        </div>
        
        <script>
        function testAPI() {
            fetch('/api/profile/current')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('api-result').innerHTML = 
                        '<div class="alert alert-success"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                })
                .catch(error => {
                    document.getElementById('api-result').innerHTML = 
                        '<div class="alert alert-danger">Error: ' + error + '</div>';
                });
        }
        </script>
    </body>
    </html>
    """

@app.route('/api/profile/current')
def api_profile_current():
    """API: Get current user profile"""
    return jsonify({
        'success': True,
        'user': dict(g.user),
        'message': 'Profile API working!'
    })

if __name__ == '__main__':
    print("🚀 Starting Profile Test Server...")
    print("📍 URL: http://localhost:3000")
    print("👤 Testing Profile system")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=3000, debug=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        # Try different port
        try:
            app.run(host='0.0.0.0', port=3001, debug=True)
        except:
            print("❌ Could not start server on any port")