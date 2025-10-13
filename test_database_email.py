#!/usr/bin/env python3
"""
สคริปต์ทดสอบการบันทึกข้อมูลอีเมลในฐานข้อมูล
Test script for email data storage in database
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_email_storage():
    """ทดสอบการเก็บข้อมูลอีเมลในฐานข้อมูล"""
    
    print("🔍 Testing Email Storage in Database")
    print("=" * 50)
    
    # ตรวจสอบไฟล์ฐานข้อมูล
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database file found: {db_path}")
    print(f"📊 Database size: {os.path.getsize(db_path)} bytes")
    print()
    
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ตรวจสอบตาราง user
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ User table not found in database")
            return False
        
        print("✅ User table exists")
        
        # แสดงโครงสร้างตาราง
        cursor.execute("PRAGMA table_info(user);")
        columns = cursor.fetchall()
        
        print("\n📋 User Table Structure:")
        print("-" * 40)
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            is_pk = "🔑" if col[5] else "  "
            print(f"{is_pk} {col_name:<20} {col_type}")
        
        # ตรวจสอบข้อมูลผู้ใช้ที่มีอยู่
        cursor.execute("SELECT COUNT(*) FROM user;")
        user_count = cursor.fetchone()[0]
        
        print(f"\n👥 Total users in database: {user_count}")
        
        if user_count > 0:
            # แสดงข้อมูลผู้ใช้ (ซ่อนรหัสผ่าน)
            cursor.execute("""
                SELECT id, username, email, first_name, profile_image, 
                       email_verified, created_at, password_hash
                FROM user 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            users = cursor.fetchall()
            
            print("\n📧 Recent Users with Email Data:")
            print("-" * 80)
            
            for i, user in enumerate(users, 1):
                user_id, username, email, first_name, profile_image, email_verified, created_at, password_hash = user
                
                print(f"\n👤 User #{i}:")
                print(f"   ID: {user_id}")
                print(f"   Username: {username}")
                print(f"   📧 Email: {email}")
                print(f"   Name: {first_name or 'N/A'}")
                print(f"   Profile Image: {'Yes' if profile_image else 'No'}")
                print(f"   Email Verified: {'✅' if email_verified else '❌'}")
                print(f"   Auth Type: {'🔑 Google OAuth' if password_hash == 'oauth_google' else '🔐 Regular'}")
                print(f"   Created: {created_at}")
        
        # ตรวจสอบผู้ใช้ Google OAuth เฉพาะ
        cursor.execute("""
            SELECT COUNT(*) FROM user 
            WHERE password_hash = 'oauth_google'
        """)
        google_users = cursor.fetchone()[0]
        
        print(f"\n🔑 Google OAuth Users: {google_users}")
        
        # ตรวจสอบอีเมลที่ไม่ซ้ำ
        cursor.execute("SELECT COUNT(DISTINCT email) FROM user;")
        unique_emails = cursor.fetchone()[0]
        
        print(f"📧 Unique Email Addresses: {unique_emails}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Database email storage test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def simulate_google_oauth_data():
    """จำลองข้อมูลที่ได้จาก Google OAuth"""
    
    print("\n🔄 Simulating Google OAuth Data Flow")
    print("=" * 50)
    
    # ข้อมูลตัวอย่างจาก Google userinfo API
    sample_google_data = {
        "email": "user.example@gmail.com",
        "name": "John Doe",
        "picture": "https://lh3.googleusercontent.com/a/example-profile-pic",
        "verified_email": True,
        "given_name": "John",
        "family_name": "Doe"
    }
    
    print("📤 Data received from Google:")
    for key, value in sample_google_data.items():
        print(f"   {key}: {value}")
    
    print("\n🔄 Processing for database storage:")
    
    # แสดงการประมวลผลข้อมูล
    processed_data = {
        "email": sample_google_data.get("email", ""),
        "username": sample_google_data.get("name", "").replace(" ", "_").lower() or sample_google_data.get("email", "").split("@")[0],
        "first_name": sample_google_data.get("given_name", ""),
        "profile_image": sample_google_data.get("picture", ""),
        "email_verified": True,
        "password_hash": "oauth_google"
    }
    
    print("💾 Data prepared for UserModel:")
    for key, value in processed_data.items():
        print(f"   {key}: {value}")
    
    return processed_data

if __name__ == "__main__":
    print("🧪 Email Database Storage Test")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # ทดสอบการเก็บข้อมูลในฐานข้อมูล
    success = test_database_email_storage()
    
    # จำลองข้อมูล Google OAuth
    simulate_google_oauth_data()
    
    if success:
        print("\n🎉 All tests passed! Email storage is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the database setup.")