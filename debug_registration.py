#!/usr/bin/env python3
"""
สคริปต์ทดสอบการบันทึกข้อมูลผู้ใช้ในฐานข้อมูล
Debug script for user registration and database storage
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_database_connection():
    """ตรวจสอบการเชื่อมต่อฐานข้อมูล"""
    
    print("🔍 Debug Database Connection")
    print("=" * 50)
    
    # ตรวจสอบไฟล์ฐานข้อมูลหลายๆ ตำแหน่ง
    db_paths = [
        os.path.join(os.path.dirname(__file__), 'instance', 'site.db'),
        os.path.join(os.path.dirname(__file__), 'database', 'instance', 'site.db'),
        os.path.join(os.path.dirname(__file__), 'app', 'instance', 'site.db')
    ]
    
    print("📍 Checking database locations:")
    for i, path in enumerate(db_paths, 1):
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   {i}. ✅ FOUND: {path} ({size} bytes)")
            
            # ตรวจสอบข้อมูลในฐานข้อมูล
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                
                # ตรวจสอบตาราง user
                cursor.execute("SELECT COUNT(*) FROM user")
                user_count = cursor.fetchone()[0]
                print(f"      👥 Users: {user_count}")
                
                # ตรวจสอบการแก้ไขล่าสุด
                cursor.execute("SELECT created_at FROM user ORDER BY created_at DESC LIMIT 1")
                latest = cursor.fetchone()
                if latest:
                    print(f"      📅 Latest user: {latest[0]}")
                else:
                    print(f"      📅 No users found")
                
                conn.close()
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
        else:
            print(f"   {i}. ❌ NOT FOUND: {path}")
    
    return db_paths

def check_google_oauth_flow():
    """ตรวจสอบการทำงานของ Google OAuth"""
    
    print(f"\n🔐 Debug Google OAuth Flow")
    print("-" * 40)
    
    # ตรวจสอบไฟล์ client_secrets.json
    client_secret_files = [
        'client_secrets.json',
        'client_secret_408122418839-0s7eoqav9dl2ounlekripelnmjhk31v7.apps.googleusercontent.com (1).json'
    ]
    
    print("🔑 OAuth Configuration Files:")
    for file in client_secret_files:
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            print(f"   ✅ FOUND: {file}")
            
            # ตรวจสอบเนื้อหาไฟล์
            try:
                import json
                with open(path, 'r') as f:
                    data = json.load(f)
                
                if 'web' in data:
                    client_id = data['web'].get('client_id', 'N/A')[:20] + '...'
                    print(f"      Client ID: {client_id}")
                    
                    redirect_uris = data['web'].get('redirect_uris', [])
                    print(f"      Redirect URIs: {len(redirect_uris)} configured")
                    for uri in redirect_uris:
                        print(f"        - {uri}")
                        
            except Exception as e:
                print(f"      ❌ Error reading: {e}")
        else:
            print(f"   ❌ NOT FOUND: {file}")

def test_manual_user_creation():
    """ทดสอบการสร้างผู้ใช้ด้วยตนเอง"""
    
    print(f"\n🧪 Test Manual User Creation")
    print("-" * 40)
    
    # หาฐานข้อมูลที่ใช้งานจริง
    db_path = None
    test_paths = [
        os.path.join(os.path.dirname(__file__), 'database', 'instance', 'site.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No database found for testing")
        return False
    
    print(f"✅ Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # สร้างผู้ใช้ทดสอบ
        import uuid
        test_user_id = str(uuid.uuid4())
        test_data = {
            'id': test_user_id,
            'username': 'testuser123',
            'email': 'testuser123@internal.system',
            'password_hash': 'oauth_google',
            'first_name': 'testuser123',
            'last_name': '',
            'email_verified': True,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        print("📝 Creating test user...")
        cursor.execute("""
            INSERT INTO user (id, username, email, password_hash, first_name, last_name, 
                            email_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_data['id'], test_data['username'], test_data['email'], 
            test_data['password_hash'], test_data['first_name'], test_data['last_name'],
            test_data['email_verified'], test_data['created_at'], test_data['updated_at']
        ))
        
        conn.commit()
        print("✅ Test user created successfully")
        
        # ตรวจสอบการบันทึก
        cursor.execute("SELECT COUNT(*) FROM user WHERE id = ?", (test_user_id,))
        count = cursor.fetchone()[0]
        
        if count == 1:
            print("✅ User data verified in database")
            
            # แสดงข้อมูลที่บันทึก
            cursor.execute("SELECT username, email, first_name FROM user WHERE id = ?", (test_user_id,))
            user_data = cursor.fetchone()
            print(f"   Username: {user_data[0]}")
            print(f"   Email: {user_data[1]}")
            print(f"   First Name: {user_data[2]}")
            
            # ลบผู้ใช้ทดสอบ
            cursor.execute("DELETE FROM user WHERE id = ?", (test_user_id,))
            conn.commit()
            print("🗑️ Test user cleaned up")
            
        else:
            print("❌ User data not found after creation")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def check_flask_logs():
    """ตรวจสอบ log ของ Flask"""
    
    print(f"\n📋 Check Flask Application Logs")
    print("-" * 40)
    
    print("💡 To debug Google OAuth registration:")
    print("1. เปิด browser ไปที่: http://localhost:5003")
    print("2. กดปุ่ม 'Login with Google'")
    print("3. ดู terminal ที่รัน Flask server")
    print("4. มองหา log messages เหล่านี้:")
    print("   - 'Creating new user from Google OAuth'")
    print("   - 'New user created with ID: ...'")
    print("   - Database connection errors")
    print("   - OAuth callback errors")
    
    print(f"\n🔍 Common Issues:")
    print("❓ ไม่มี log แสดง → OAuth callback ไม่ถูกเรียก")
    print("❓ 'Database connection error' → ปัญหาการเชื่อมต่อฐานข้อมูล")
    print("❓ 'User creation failed' → ปัญหาการสร้างผู้ใช้")
    print("❓ 'OAuth token fetch failed' → ปัญหา Google OAuth config")

def main():
    """ฟังก์ชันหลัก"""
    
    print("🔧 Debug: User Registration Not Saving to Database")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # ตรวจสอบฐานข้อมูล
    db_paths = debug_database_connection()
    
    # ตรวจสอบ Google OAuth
    check_google_oauth_flow()
    
    # ทดสอบการสร้างผู้ใช้
    db_test = test_manual_user_creation()
    
    # แนะนำการ debug
    check_flask_logs()
    
    print(f"\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY:")
    
    if db_test:
        print("✅ Database connection and user creation: WORKING")
        print("🔍 Issue likely in Google OAuth flow or Flask routing")
        print()
        print("📋 Next Steps:")
        print("1. ลองล็อกอินผ่าน Google: http://localhost:5003/auth/google")
        print("2. ดู Flask server logs ใน terminal")
        print("3. ตรวจสอบว่า callback URL ถูกต้องใน Google Console")
        print("4. ตรวจสอบว่า client_secrets.json ถูกต้อง")
    else:
        print("❌ Database connection issue detected")
        print("🔧 Fix database setup first, then try OAuth again")

if __name__ == "__main__":
    main()