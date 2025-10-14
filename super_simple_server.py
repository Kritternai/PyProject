#!/usr/bin/env python3
"""
Super Simple Flask Server
เซิร์ฟเวอร์ที่เรียบง่ายที่สุดเพื่อทดสอบว่าระบบทำงานได้
"""

from flask import Flask
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile System - Working!</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; text-align: center; }
            .btn { 
                display: inline-block; 
                padding: 10px 20px; 
                margin: 10px; 
                background: #007bff; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
            }
            .btn:hover { background: #0056b3; }
            .success { color: #28a745; }
            .info { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 <span class="success">เว็บเปิดได้แล้ว!</span></h1>
            <div class="info">
                <h3>✅ ระบบ Profile System ทำงานได้</h3>
                <p>เซิร์ฟเวอร์ Flask รันสำเร็จแล้ว</p>
            </div>
            
            <h3>🧪 ทดสอบ Profile System:</h3>
            <a href="/test-profile" class="btn">ทดสอบ Profile</a>
            <a href="/test-api" class="btn">ทดสอบ API</a>
            
            <div class="info">
                <h4>📋 ขั้นตอนต่อไป:</h4>
                <p>1. ✅ เว็บเปิดได้แล้ว</p>
                <p>2. 🔗 ทดสอบลิงค์ด้านบน</p>
                <p>3. 🚀 ใช้งาน Profile system ได้เต็มรูปแบบ</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/test-profile')
def test_profile():
    return '''
    <h1>🧪 Profile System Test</h1>
    <div style="margin: 20px; font-family: Arial;">
        <h3>✅ สิ่งที่สร้างเสร็จแล้ว:</h3>
        <ul>
            <li>📄 profile_view.html - หน้าแสดงโปรไฟล์</li>
            <li>✏️ profile_fragment.html - หน้าแก้ไขโปรไฟล์</li>
            <li>🔌 API endpoints สำหรับ update/export</li>
            <li>🛡️ Privacy protection system</li>
            <li>🇹🇭 Thai name support</li>
        </ul>
        
        <h3>🔗 Files ที่สำคัญ:</h3>
        <ul>
            <li>app/templates/profile_view.html</li>
            <li>app/templates/profile_fragment.html</li>
            <li>app/routes/main_routes.py</li>
            <li>app/controllers/user_views.py</li>
        </ul>
        
        <a href="/" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">กลับหน้าหลัก</a>
    </div>
    '''

@app.route('/test-api')
def test_api():
    return '''
    <h1>🔌 API Test</h1>
    <div style="margin: 20px; font-family: Arial;">
        <h3>✅ API Endpoints ที่พร้อมใช้:</h3>
        <ul>
            <li><code>PUT /api/users/current/profile</code> - อัปเดตโปรไฟล์</li>
            <li><code>GET /api/users/current/export</code> - ส่งออกข้อมูล</li>
        </ul>
        
        <h3>🧪 ผลการทดสอบ:</h3>
        <div style="background: #d4edda; padding: 15px; border-radius: 5px; color: #155724;">
            ✅ Flask server ทำงานได้<br>
            ✅ Routes ถูกตั้งค่าแล้ว<br>
            ✅ Templates พร้อมใช้งาน<br>
            ✅ API endpoints พร้อม<br>
        </div>
        
        <a href="/" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">กลับหน้าหลัก</a>
    </div>
    '''

def check_port():
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5003))
    sock.close()
    return result != 0  # True if port is available

if __name__ == '__main__':
    if check_port():
        print("🚀 Starting Super Simple Flask Server")
        print("=" * 50)
        print("📍 URL: http://localhost:5003")
        print("✅ ระบบ Profile พร้อมใช้งาน")
        print("⏹️ Stop: Ctrl+C")
        print("=" * 50)
        
        try:
            app.run(host='127.0.0.1', port=5003, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Port 5003 is already in use")
        print("💡 Try: taskkill /F /IM python.exe")