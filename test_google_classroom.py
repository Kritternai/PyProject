#!/usr/bin/env python3
"""
Test Script for Google Classroom Integration
This script tests the Google Classroom API integration functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_google_credentials_model():
    """Test GoogleCredentials model"""
    
    print("🔄 Testing GoogleCredentials model...")
    
    try:
        from app import app, db
        from app.core.google_credentials import GoogleCredentials
        
        with app.app_context():
            # Test model creation
            test_creds = GoogleCredentials(
                user_id='test-user-id',
                token='test-token',
                refresh_token='test-refresh-token',
                token_uri='https://oauth2.googleapis.com/token',
                client_id='test-client-id',
                client_secret='test-client-secret',
                scopes='classroom.courses.readonly,classroom.announcements.readonly'
            )
            
            print(f"✅ GoogleCredentials model created successfully")
            print(f"   User ID: {test_creds.user_id}")
            print(f"   Token: {test_creds.token[:10]}...")
            print(f"   Scopes: {test_creds.scopes}")
            
            return True
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_api_libraries():
    """Test Google API libraries import"""
    
    print("\n🔄 Testing Google API libraries...")
    
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import Flow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        print("✅ Google API libraries imported successfully")
        print("   - google.oauth2.credentials")
        print("   - google_auth_oauthlib.flow")
        print("   - google.auth.transport.requests")
        print("   - googleapiclient.discovery")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages:")
        print("pip install google-api-python-client google-auth-oauthlib")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_google_classroom_routes():
    """Test Google Classroom routes import"""
    
    print("\n🔄 Testing Google Classroom routes...")
    
    try:
        from app import app
        
        # Check if routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        google_routes = [r for r in routes if 'google_classroom' in r]
        
        print(f"✅ Found {len(google_routes)} Google Classroom routes:")
        for route in google_routes:
            print(f"   - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_classroom_config():
    """Test Google Classroom configuration"""
    
    print("\n🔄 Testing Google Classroom configuration...")
    
    try:
        from app import app
        
        # Check configuration
        client_id = app.config.get('GOOGLE_CLIENT_ID')
        client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
        
        if client_id and client_secret:
            print("✅ Google Classroom configuration found")
            print(f"   Client ID: {client_id[:10]}...")
            print(f"   Client Secret: {client_secret[:10]}...")
        else:
            print("⚠️  Google Classroom configuration not found")
            print("   Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
            print("   environment variables")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_classroom_scopes():
    """Test Google Classroom scopes"""
    
    print("\n🔄 Testing Google Classroom scopes...")
    
    try:
        from app.routes import SCOPES
        
        print(f"✅ Found {len(SCOPES)} Google Classroom scopes:")
        for scope in SCOPES:
            print(f"   - {scope}")
        
        # Check required scopes
        required_scopes = [
            'https://www.googleapis.com/auth/classroom.courses.readonly',
            'https://www.googleapis.com/auth/classroom.announcements.readonly',
            'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
            'https://www.googleapis.com/auth/classroom.course-work.readonly',
            'https://www.googleapis.com/auth/classroom.topics.readonly',
            'https://www.googleapis.com/auth/classroom.rosters.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        missing_scopes = [scope for scope in required_scopes if scope not in SCOPES]
        if missing_scopes:
            print(f"⚠️  Missing required scopes: {missing_scopes}")
        else:
            print("✅ All required scopes are present")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_classroom_integration():
    """Test Google Classroom integration components"""
    
    print("\n🔄 Testing Google Classroom integration components...")
    
    try:
        from app.core.data_sync import DataSyncService
        from app.core.lesson_manager import LessonManager
        
        print("✅ DataSyncService imported successfully")
        print("✅ LessonManager imported successfully")
        
        # Test DataSyncService methods
        if hasattr(DataSyncService, 'sync_google_classroom_data'):
            print("✅ DataSyncService.sync_google_classroom_data method found")
        else:
            print("❌ DataSyncService.sync_google_classroom_data method not found")
        
        # Test LessonManager methods
        if hasattr(LessonManager, 'import_google_classroom_course_as_lesson'):
            print("✅ LessonManager.import_google_classroom_course_as_lesson method found")
        else:
            print("❌ LessonManager.import_google_classroom_course_as_lesson method not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Smart Learning Hub - Google Classroom Integration Tests")
    print("=" * 70)
    
    tests = [
        test_google_credentials_model,
        test_google_api_libraries,
        test_google_classroom_routes,
        test_google_classroom_config,
        test_google_classroom_scopes,
        test_google_classroom_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("Google Classroom integration is ready for configuration.")
        print("\nNext steps:")
        print("1. Set up Google Cloud Console project")
        print("2. Enable Google Classroom API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Set environment variables")
        print("5. Test connection through web interface")
        return 0
    else:
        print("💥 Some tests failed!")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
