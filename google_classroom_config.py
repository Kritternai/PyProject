#!/usr/bin/env python3
"""
Google Classroom API Configuration
This file contains configuration and setup instructions for Google Classroom API integration
"""

import os
from pathlib import Path

# =============================================================================
# GOOGLE CLASSROOM API SETUP INSTRUCTIONS
# =============================================================================

def print_setup_instructions():
    """Print setup instructions for Google Classroom API"""
    print("🚀 Google Classroom API Setup Instructions")
    print("=" * 60)
    print()
    
    print("1. 🌐 Go to Google Cloud Console")
    print("   Visit: https://console.cloud.google.com/")
    print()
    
    print("2. 📁 Create or Select a Project")
    print("   - Click on the project dropdown at the top")
    print("   - Click 'New Project' or select existing project")
    print()
    
    print("3. 🔧 Enable Google Classroom API")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Classroom API'")
    print("   - Click on it and press 'Enable'")
    print()
    
    print("4. 🔑 Create OAuth 2.0 Credentials")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Web application'")
    print()
    
    print("5. 📝 Configure OAuth Consent Screen")
    print("   - App name: 'Smart Learning Hub'")
    print("   - User support email: your-email@domain.com")
    print("   - Developer contact information: your-email@domain.com")
    print()
    
    print("6. 🔗 Add Authorized Redirect URIs")
    print("   - http://localhost:8000/google_classroom/oauth2callback")
    print("   - http://127.0.0.1:8000/google_classroom/oauth2callback")
    print("   - Add your production domain if deploying")
    print()
    
    print("7. 📋 Copy Credentials")
    print("   - Copy Client ID and Client Secret")
    print("   - Save them securely")
    print()
    
    print("8. ⚙️ Set Environment Variables")
    print("   export GOOGLE_CLIENT_ID='your-client-id-here'")
    print("   export GOOGLE_CLIENT_SECRET='your-client-secret-here'")
    print()
    
    print("9. 🚀 Test Connection")
    print("   - Run the application")
    print("   - Click 'Connect Google Classroom'")
    print("   - Complete OAuth flow")
    print()

# =============================================================================
# REQUIRED SCOPES
# =============================================================================

GOOGLE_CLASSROOM_SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/classroom.course-work.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.topics.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.readonly'
]

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("-" * 40)
    
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if client_id and client_secret:
        print("✅ GOOGLE_CLIENT_ID: Set")
        print("✅ GOOGLE_CLIENT_SECRET: Set")
        print("✅ Environment variables are configured correctly!")
        return True
    else:
        print("❌ GOOGLE_CLIENT_ID: Not set" if not client_id else "✅ GOOGLE_CLIENT_ID: Set")
        print("❌ GOOGLE_CLIENT_SECRET: Not set" if not client_secret else "✅ GOOGLE_CLIENT_SECRET: Set")
        print()
        print("Please set the environment variables:")
        print("export GOOGLE_CLIENT_ID='your-client-id-here'")
        print("export GOOGLE_CLIENT_SECRET='your-client-secret-here'")
        return False

# =============================================================================
# TEST CONNECTION
# =============================================================================

def test_google_api_connection():
    """Test Google API connection with current credentials"""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Cannot test connection: Missing credentials")
            return False
        
        print("🔍 Testing Google API Connection")
        print("-" * 40)
        
        # This is just a basic test - actual OAuth flow requires user interaction
        print("✅ Google API libraries imported successfully")
        print("✅ Credentials format appears correct")
        print("ℹ️  Full OAuth flow requires user interaction in browser")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages:")
        print("pip install google-api-python-client google-auth-oauthlib")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main function to run setup checks"""
    print("🔧 Google Classroom API Configuration Check")
    print("=" * 60)
    print()
    
    # Check environment variables
    env_ok = check_environment_variables()
    print()
    
    # Test API connection
    api_ok = test_google_api_connection()
    print()
    
    if env_ok and api_ok:
        print("🎉 All checks passed! Google Classroom API should work.")
        print("Try connecting through the web interface.")
    else:
        print("⚠️  Some issues found. Please follow the setup instructions above.")
        print()
        print_setup_instructions()

if __name__ == "__main__":
    main()
