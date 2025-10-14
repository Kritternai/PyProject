#!/usr/bin/env python3
"""
Real-time OAuth Monitor
ติดตามการทำงานของ OAuth แบบ real-time
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

def monitor_database():
    print("🔍 Real-time OAuth Database Monitor")
    print("=" * 60)
    print("📊 Starting monitor... (Ctrl+C to stop)")
    print("💡 Try Google OAuth login in browser now!")
    print()
    
    db_path = Path("instance/site.db")
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    # Get initial user count
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user")
    initial_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"🎯 Initial user count: {initial_count}")
    print("⏰ Monitoring for new users...")
    print()
    
    last_count = initial_count
    
    try:
        while True:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check current user count
            cursor.execute("SELECT COUNT(*) FROM user")
            current_count = cursor.fetchone()[0]
            
            if current_count > last_count:
                print(f"🎉 NEW USER DETECTED! Count: {last_count} → {current_count}")
                
                # Get the newest user
                cursor.execute("""
                    SELECT id, username, email, password_hash, created_at, first_name
                    FROM user 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """)
                
                new_user = cursor.fetchone()
                if new_user:
                    user_id, username, email, password_hash, created_at, first_name = new_user
                    
                    print("👤 New User Details:")
                    print(f"   🆔 ID: {user_id}")
                    print(f"   👤 Username: {username}")
                    print(f"   📧 Email: {email}")
                    print(f"   🔐 Auth Type: {'Google OAuth' if password_hash == 'oauth_google' else 'Regular'}")
                    print(f"   👋 Name: {first_name}")
                    print(f"   ⏰ Created: {created_at}")
                    print()
                
                last_count = current_count
            
            conn.close()
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitor stopped")
        
        # Final summary
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n📊 Final Summary:")
        print(f"   Initial users: {initial_count}")
        print(f"   Final users: {final_count}")
        print(f"   New users created: {final_count - initial_count}")
        
        if final_count > initial_count:
            print("✅ OAuth registration is working!")
        else:
            print("❓ No new users created during monitoring")

if __name__ == "__main__":
    monitor_database()