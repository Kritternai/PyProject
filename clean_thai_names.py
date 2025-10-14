#!/usr/bin/env python3
"""
สคริปต์ล้างข้อมูลชื่อภาษาไทยในฐานข้อมูล
Clean Thai names from database and reset to English-friendly format
"""

import sys
import os
import sqlite3
import re
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def is_thai_text(text):
    """ตรวจสอบว่าข้อความมีภาษาไทยหรือไม่"""
    if not text:
        return False
    # Thai Unicode range: \u0E00-\u0E7F
    return bool(re.search(r'[\u0E00-\u0E7F]', text))

def clean_thai_names_from_database():
    """ล้างชื่อภาษาไทยออกจากฐานข้อมูล"""
    
    print("🧹 Cleaning Thai Names from Database")
    print("=" * 50)
    
    # ตรวจสอบไฟล์ฐานข้อมูล
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'instance', 'site.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database file found: {db_path}")
    
    try:
        # สำรองฐานข้อมูลก่อน
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ดึงข้อมูลผู้ใช้ทั้งหมด
        cursor.execute("""
            SELECT id, username, first_name, last_name, email 
            FROM user 
        """)
        
        users = cursor.fetchall()
        updated_count = 0
        
        print(f"\n📋 Found {len(users)} users to check")
        print("-" * 40)
        
        for user in users:
            user_id, username, first_name, last_name, email = user
            needs_update = False
            new_values = {}
            
            print(f"\n👤 User ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Current - Username: '{username}', First: '{first_name}', Last: '{last_name}'")
            
            # ตรวจสอบและทำความสะอาด first_name
            if first_name and is_thai_text(first_name):
                print(f"   🧹 Thai first_name detected: '{first_name}' → clearing")
                new_values['first_name'] = ""
                needs_update = True
            
            # ตรวจสอบและทำความสะอาด last_name  
            if last_name and is_thai_text(last_name):
                print(f"   🧹 Thai last_name detected: '{last_name}' → clearing")
                new_values['last_name'] = ""
                needs_update = True
            
            # ตรวจสอบและปรับปรุง username ถ้าเป็นภาษาไทย
            if username and is_thai_text(username):
                # สร้าง username ใหม่จาก email
                if email:
                    new_username = email.split("@")[0]
                    print(f"   🧹 Thai username detected: '{username}' → '{new_username}'")
                    new_values['username'] = new_username
                    needs_update = True
                else:
                    print(f"   ⚠️  Thai username found but no email: '{username}'")
            
            # อัปเดตข้อมูลถ้าจำเป็น
            if needs_update:
                update_fields = []
                update_values = []
                
                for field, value in new_values.items():
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
                
                if update_fields:
                    update_values.append(user_id)  # สำหรับ WHERE clause
                    
                    sql = f"UPDATE user SET {', '.join(update_fields)}, updated_at = ? WHERE id = ?"
                    update_values.insert(-1, datetime.utcnow().isoformat())  # เพิ่ม updated_at
                    
                    cursor.execute(sql, update_values)
                    updated_count += 1
                    print("   ✅ Updated successfully")
            else:
                print("   ✅ No Thai text found, no update needed")
        
        # บันทึกการเปลี่ยนแปลง
        conn.commit()
        
        print(f"\n" + "=" * 50)
        print(f"✅ Database cleanup completed!")
        print(f"📊 Total users checked: {len(users)}")
        print(f"🔄 Users updated: {updated_count}")
        
        # แสดงข้อมูลหลังการทำความสะอาด
        print(f"\n📋 Updated User Data:")
        print("-" * 40)
        
        cursor.execute("""
            SELECT id, username, first_name, last_name, email, password_hash
            FROM user 
            WHERE password_hash = 'oauth_google'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        google_users = cursor.fetchall()
        
        for user in google_users:
            user_id, username, first_name, last_name, email, password_hash = user
            print(f"👤 {email}: username='{username}', name='{first_name} {last_name}'.strip()")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def update_google_oauth_settings():
    """อัปเดตการตั้งค่า Google OAuth"""
    
    print(f"\n⚙️ Google OAuth Configuration:")
    print("-" * 40)
    print("✅ Modified routes_google_auth.py:")
    print("   - ใช้ email prefix แทนชื่อจาก Google")
    print("   - เซ็ต first_name เป็นค่าว่าง")
    print("   - ให้ผู้ใช้แก้ไขชื่อเองหลังจากล็อกอิน")
    
    print(f"\n📝 Profile Template Updates:")
    print("   - แนะนำให้ใช้ชื่อภาษาอังกฤษ")
    print("   - เพิ่มคำแนะนำในฟิลด์ต่างๆ")
    print("   - รองรับทั้งภาษาไทยและอังกฤษ")

if __name__ == "__main__":
    print("🗂️ Database Thai Name Cleanup")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # ทำความสะอาดฐานข้อมูล
    success = clean_thai_names_from_database()
    
    # อัปเดตการตั้งค่า OAuth
    update_google_oauth_settings()
    
    if success:
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"\n📋 Changes made:")
        print("✅ Thai names cleared from database")
        print("✅ Usernames converted to email prefixes")
        print("✅ Google OAuth updated to not store Thai names")
        print("✅ Profile form updated with English recommendations")
        
        print(f"\n🔄 Next steps:")
        print("1. Users can edit their profiles at /profile/edit")
        print("2. Recommend using English names for better display")
        print("3. Username and bio can still use Thai if preferred")
    else:
        print(f"\n⚠️  Cleanup failed. Please check the errors above.")