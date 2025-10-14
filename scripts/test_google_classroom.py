#!/usr/bin/env python3
"""
Test Google Classroom Integration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_google_classroom_setup():
    """Test Google Classroom setup"""
    print("🔍 Testing Google Classroom Integration")
    print("=" * 50)
    
    # Check environment variables
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    print(f"GOOGLE_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
    print(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")
    
    if not client_id or not client_secret:
        print("\n❌ Google OAuth credentials not configured!")
        print("Please set environment variables:")
        print("export GOOGLE_CLIENT_ID='your-client-id'")
        print("export GOOGLE_CLIENT_SECRET='your-client-secret'")
        return False
    
    # Check database
    try:
        import sqlite3
        db_path = project_root / 'instance' / 'site.db'
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(user)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'google_credentials' in columns:
                print("✅ Database schema: google_credentials column exists")
            else:
                print("❌ Database schema: google_credentials column missing")
                return False
            
            conn.close()
        else:
            print("❌ Database not found")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Check Google API libraries
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        print("✅ Google API libraries: Available")
    except ImportError as e:
        print(f"❌ Google API libraries: {e}")
        return False
    
    print("\n🎉 Google Classroom integration is ready!")
    print("\nNext steps:")
    print("1. Start the application: python start_server.py")
    print("2. Go to http://localhost:5004")
    print("3. Click 'Create New Class'")
    print("4. Click 'Import from Google Classroom'")
    print("5. Complete OAuth flow")
    
    return True

if __name__ == "__main__":
    test_google_classroom_setup()
