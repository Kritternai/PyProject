"""
Google Classroom Configuration - New Complete Implementation
การตั้งค่าสำหรับ Google Classroom บน port 8000
"""

import os
from pathlib import Path

# Google Classroom API Configuration
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

# Server Configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = '0.0.0.0'

# OAuth Configuration
OAUTH_REDIRECT_URIS = [
    f"http://localhost:{DEFAULT_PORT}/google_classroom/oauth2callback",
    f"http://127.0.0.1:{DEFAULT_PORT}/google_classroom/oauth2callback",
    f"http://localhost:{DEFAULT_PORT}/google_classroom/oauth2callback",
    f"http://127.0.0.1:{DEFAULT_PORT}/google_classroom/oauth2callback"
]

# Google Cloud Console Setup Instructions
GOOGLE_CLOUD_SETUP_INSTRUCTIONS = """
🚀 Google Cloud Console Setup Instructions
==========================================

1. 🌐 Go to Google Cloud Console
   https://console.cloud.google.com/

2. 📁 Create or Select a Project
   - Click on the project dropdown at the top
   - Click 'New Project' or select existing project

3. 🔧 Enable Google Classroom API
   - Go to 'APIs & Services' > 'Library'
   - Search for 'Google Classroom API'
   - Click on it and press 'Enable'

4. 🔑 Create OAuth 2.0 Credentials
   - Go to 'APIs & Services' > 'Credentials'
   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'
   - Choose 'Web application'

5. 📝 Configure OAuth Consent Screen
   - App name: 'Smart Learning Hub'
   - User support email: your-email@domain.com
   - Developer contact information: your-email@domain.com

6. 🔗 Add Authorized Redirect URIs
   - http://localhost:8000/google_classroom/oauth2callback
   - http://127.0.0.1:8000/google_classroom/oauth2callback

7. 📋 Copy Credentials
   - Copy Client ID and Client Secret
   - Save them securely

8. ⚙️ Set Environment Variables
   export GOOGLE_CLIENT_ID='your-client-id-here'
   export GOOGLE_CLIENT_SECRET='your-client-secret-here'

9. 🚀 Test Connection
   - Run the application on port 8000
   - Click 'Import from Google Classroom'
   - Complete OAuth flow
"""

def get_oauth_config(port=DEFAULT_PORT):
    """Get OAuth configuration for specified port"""
    return {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uris': [
            f"http://localhost:{port}/google_classroom/oauth2callback",
            f"http://127.0.0.1:{port}/google_classroom/oauth2callback"
        ],
        'scopes': GOOGLE_CLASSROOM_SCOPES
    }

def validate_oauth_config():
    """Validate OAuth configuration"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return False, "Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET"
    
    if not client_id.endswith('.apps.googleusercontent.com'):
        return False, "Invalid GOOGLE_CLIENT_ID format"
    
    if not client_secret.startswith('GOCSPX-'):
        return False, "Invalid GOOGLE_CLIENT_SECRET format"
    
    return True, "Configuration is valid"

def print_setup_instructions():
    """Print setup instructions"""
    print(GOOGLE_CLOUD_SETUP_INSTRUCTIONS)
    
def print_configuration_status():
    """Print current configuration status"""
    print("🔧 Google Classroom Configuration Status")
    print("=" * 50)
    
    # Check environment variables
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    print(f"Client ID: {'✅ Set' if client_id else '❌ Not set'}")
    if client_id:
        print(f"  Value: {client_id[:30]}...")
    
    print(f"Client Secret: {'✅ Set' if client_secret else '❌ Not set'}")
    if client_secret:
        print(f"  Value: {client_secret[:10]}...")
    
    # Check configuration validity
    is_valid, message = validate_oauth_config()
    print(f"Configuration: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if not is_valid:
        print(f"  Error: {message}")
    
    # Show redirect URIs
    print(f"\nRedirect URIs:")
    for uri in OAUTH_REDIRECT_URIS:
        print(f"  - {uri}")
    
    print(f"\nServer Port: {DEFAULT_PORT}")
    print(f"Server Host: {DEFAULT_HOST}")
    
    return is_valid

if __name__ == "__main__":
    print_configuration_status()
    if not validate_oauth_config()[0]:
        print("\n" + "=" * 50)
        print_setup_instructions()
