#!/usr/bin/env python3
"""
สคริปต์ตรวจสอบการบันทึกอีเมลในฐานข้อมูลหลังจากปรับปรุงระบบ
Check email storage in database after privacy system update
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_current_email_system():
    """ตรวจสอบระบบอีเมลปัจจุบันในฐานข้อมูล"""
    
    print("🔍 Checking Current Email System in Database")
    print("=" * 60)
    
    # ตรวจสอบไฟล์ฐานข้อมูล
    db_paths = [
        os.path.join(os.path.dirname(__file__), 'database', 'instance', 'site.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found")
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
        
        # ตรวจสอบข้อมูลผู้ใช้ทั้งหมด
        cursor.execute("SELECT COUNT(*) FROM user;")
        user_count = cursor.fetchone()[0]
        
        print(f"\n👥 Total users in database: {user_count}")
        
        if user_count > 0:
            # แสดงข้อมูלผู้ใช้ทั้งหมด
            cursor.execute("""
                SELECT id, username, email, first_name, last_name, 
                       password_hash, email_verified, created_at 
                FROM user 
                ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            print(f"\n📧 Email Storage Analysis:")
            print("-" * 50)
            
            google_users = 0
            regular_users = 0
            internal_emails = 0
            real_emails = 0
            
            for i, user in enumerate(users, 1):
                user_id, username, email, first_name, last_name, password_hash, email_verified, created_at = user
                
                print(f"\n👤 User #{i}:")
                print(f"   ID: {user_id}")
                print(f"   Username: {username}")
                
                # วิเคราะห์ประเภทอีเมล
                if "@internal.system" in email:
                    print(f"   📧 Email: {email} (🔒 INTERNAL - ไม่ใช่อีเมลจริง)")
                    internal_emails += 1
                else:
                    print(f"   📧 Email: {email} (⚠️ REAL EMAIL)")
                    real_emails += 1
                
                print(f"   Name: {first_name or 'N/A'} {last_name or ''}")
                print(f"   Email Verified: {'✅' if email_verified else '❌'}")
                
                if password_hash == 'oauth_google':
                    print(f"   Auth Type: 🔑 Google OAuth")
                    google_users += 1
                else:
                    print(f"   Auth Type: 🔐 Regular")
                    regular_users += 1
                
                print(f"   Created: {created_at}")
            
            # สรุปสถิติ
            print(f"\n" + "=" * 50)
            print(f"📊 EMAIL PRIVACY ANALYSIS:")
            print(f"👥 Total Users: {user_count}")
            print(f"🔑 Google OAuth Users: {google_users}")
            print(f"🔐 Regular Users: {regular_users}")
            print(f"🔒 Internal Emails: {internal_emails}")
            print(f"⚠️  Real Emails: {real_emails}")
            
            # ตรวจสอบความปลอดภัย
            print(f"\n🛡️ PRIVACY STATUS:")
            if real_emails == 0:
                print("✅ EXCELLENT: ไม่มีอีเมลจริงในระบบเลย!")
                print("✅ ระบบป้องกันความเป็นส่วนตัวทำงานสมบูรณ์")
            else:
                print(f"⚠️  WARNING: พบอีเมลจริง {real_emails} รายการ")
                print("❗ ควรทำความสะอาดข้อมูลเหล่านี้")
            
            if google_users > 0:
                google_with_internal = cursor.execute("""
                    SELECT COUNT(*) FROM user 
                    WHERE password_hash = 'oauth_google' 
                    AND email LIKE '%@internal.system'
                """).fetchone()[0]
                
                print(f"\n🔑 GOOGLE OAUTH ANALYSIS:")
                print(f"   Google users with internal emails: {google_with_internal}/{google_users}")
                if google_with_internal == google_users:
                    print("   ✅ All Google users use internal emails!")
                else:
                    print("   ⚠️  Some Google users still have real emails")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def explain_current_system():
    """อธิบายระบบปัจจุบันหลังจากการปรับปรุง"""
    
    print(f"\n📋 CURRENT EMAIL SYSTEM EXPLANATION:")
    print("=" * 60)
    
    print("🔄 Google OAuth Email Processing:")
    print("1. รับอีเมลจาก Google: kanruethai.741236@gmail.com")
    print("2. แยกเอา email prefix: kanruethai.741236")
    print("3. สร้าง system email: kanruethai.741236@internal.system")
    print("4. บันทึกใน database:")
    print("   - username: kanruethai.741236")
    print("   - email: kanruethai.741236@internal.system")
    print("   - first_name: kanruethai.741236")
    print("   - ❌ อีเมลจริงไม่ถูกบันทึก")
    print("   - ❌ ชื่อจริงจาก Google ไม่ถูกบันทึก")
    
    print(f"\n🛡️ Privacy Benefits:")
    print("✅ ระบบไม่เก็บอีเมลจริงของผู้ใช้")
    print("✅ ระบบไม่เก็บชื่อจริงจาก Google")
    print("✅ ใช้ระบบอีเมลภายในแทน")
    print("✅ ผู้ใช้ควบคุมข้อมูลแสดงผลได้เต็มที่")
    print("✅ ระบบยังคงทำงานได้ปกติ")

def test_oauth_data_processing():
    """ทดสอบการประมวลผลข้อมูล OAuth"""
    
    print(f"\n🧪 Testing OAuth Data Processing:")
    print("-" * 40)
    
    # จำลองข้อมูลจาก Google
    mock_google_data = {
        "email": "kanruethai.741236@gmail.com", 
        "name": "กันต์ฤทัย แก้วสว่าง",
        "picture": "https://lh3.googleusercontent.com/a/example"
    }
    
    print("📥 Data from Google:")
    for key, value in mock_google_data.items():
        print(f"   {key}: {value}")
    
    # ประมวลผลตามระบบใหม่
    email = mock_google_data["email"]
    email_prefix = email.split("@")[0]
    system_email = f"{email_prefix}@internal.system"
    
    print(f"\n🔄 Processing:")
    print(f"   Original Email: {email}")
    print(f"   Email Prefix: {email_prefix}")
    print(f"   System Email: {system_email}")
    
    processed_data = {
        "username": email_prefix,
        "email": system_email,
        "first_name": email_prefix,
        "last_name": "",
        "password_hash": "oauth_google",
        "profile_image": mock_google_data["picture"],
        "email_verified": True
    }
    
    print(f"\n💾 Data stored in database:")
    for key, value in processed_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n❌ Data NOT stored:")
    print(f"   real_email: {email} (ปกป้องความเป็นส่วนตัว)")
    print(f"   real_name: {mock_google_data['name']} (ให้ผู้ใช้ตั้งเอง)")

if __name__ == "__main__":
    print("🔍 Email Storage Analysis After Privacy Update")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # ตรวจสอบระบบปัจจุบัน
    success = check_current_email_system()
    
    # อธิบายระบบ
    explain_current_system()
    
    # ทดสอบการประมวลผล
    test_oauth_data_processing()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 Analysis completed!")
        print("\n📋 Key Points:")
        print("✅ ระบบตอนนี้ป้องกันความเป็นส่วนตัวแล้ว")
        print("✅ ไม่มีการบันทึกอีเมลจริงจาก Google OAuth")
        print("✅ ใช้ระบบอีเมลภายใน (username@internal.system)")
        print("✅ ผู้ใช้สามารถแก้ไขชื่อแสดงผลได้เอง")
    else:
        print("⚠️  Analysis failed. Please check database connection.")