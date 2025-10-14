#!/usr/bin/env python3
"""
Check OAuth Error Details
ตรวจสอบรายละเอียดข้อผิดพลาดในการ OAuth
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def main():
    print("🔍 Checking OAuth Error Details")
    print("=" * 60)
    
    # Check recent users
    db_path = Path("instance/site.db")
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all users with details
    cursor.execute("""
        SELECT id, username, email, password_hash, created_at, updated_at, 
               first_name, last_name, role, is_active, email_verified
        FROM user 
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    print(f"📊 Total users in database: {len(users)}")
    print("\n📋 User List:")
    
    for i, user in enumerate(users, 1):
        user_id, username, email, password_hash, created_at, updated_at, first_name, last_name, role, is_active, email_verified = user
        print(f"\n👤 User {i}:")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password Hash: {password_hash[:20]}..." if password_hash else "   Password Hash: None")
        print(f"   Name: {first_name} {last_name or ''}")
        print(f"   Role: {role}")
        print(f"   Active: {is_active}")
        print(f"   Email Verified: {email_verified}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        
        # Check if OAuth user
        if password_hash == "oauth_google":
            print(f"   🔐 Type: Google OAuth User")
        elif email and "@internal.system" in email:
            print(f"   🔐 Type: Internal System User (possibly OAuth)")
        else:
            print(f"   🔐 Type: Regular User")
    
    conn.close()
    
    # Check client_secrets.json
    print("\n" + "=" * 60)
    print("🔑 OAuth Configuration Check:")
    
    secrets_path = Path("client_secrets.json")
    if secrets_path.exists():
        try:
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
            
            if 'web' in secrets:
                client_id = secrets['web'].get('client_id', 'N/A')
                redirect_uris = secrets['web'].get('redirect_uris', [])
                
                print(f"✅ Client ID: {client_id[:20]}...")
                print(f"✅ Redirect URIs:")
                for uri in redirect_uris:
                    print(f"   - {uri}")
            else:
                print("❌ Invalid client_secrets.json format")
        except Exception as e:
            print(f"❌ Error reading client_secrets.json: {e}")
    else:
        print("❌ client_secrets.json not found")
    
    # Check for common OAuth issues
    print("\n" + "=" * 60)
    print("🚨 Common OAuth Issues to Check:")
    print("1. Browser Console Errors:")
    print("   - Open F12 → Console tab when doing OAuth")
    print("   - Look for JavaScript errors or network failures")
    print("\n2. Flask Server Terminal:")
    print("   - Check for error messages during OAuth callback")
    print("   - Look for database connection errors")
    print("\n3. Google OAuth Console:")
    print("   - Verify redirect URI is exactly: http://localhost:5003/auth/google/callback")
    print("   - Check if OAuth consent screen is configured")
    print("\n4. Network Issues:")
    print("   - Firewall blocking localhost:5003")
    print("   - Antivirus software interfering")
    
    print("\n" + "=" * 60)
    print("💡 Next Steps:")
    print("1. Try OAuth again and watch Flask terminal for errors")
    print("2. Check browser console (F12) during OAuth")
    print("3. Verify Google OAuth settings match redirect URI")

if __name__ == "__main__":
    main()