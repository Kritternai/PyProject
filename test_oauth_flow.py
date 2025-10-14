#!/usr/bin/env python3
"""
Test Google OAuth Flow
ทดสอบขั้นตอนการ OAuth และดู logs
"""

import requests
import time
from urllib.parse import urljoin

def test_oauth_flow():
    print("🧪 Testing Google OAuth Flow")
    print("=" * 60)
    
    base_url = "http://localhost:5003"
    
    # Test 1: Check if server is running
    print("📡 Test 1: Server Health Check")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server on localhost:5003")
        print("💡 Make sure Flask server is running")
        return
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return
    
    # Test 2: Check OAuth login endpoint
    print("\n🔐 Test 2: OAuth Login Endpoint")
    try:
        oauth_url = urljoin(base_url, "/auth/google/login")
        response = requests.get(oauth_url, timeout=5, allow_redirects=False)
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if 'accounts.google.com' in redirect_url:
                print("✅ OAuth login endpoint working - redirects to Google")
                print(f"📍 Redirect URL: {redirect_url[:100]}...")
            else:
                print(f"⚠️ OAuth redirects but not to Google: {redirect_url}")
        else:
            print(f"❌ OAuth login endpoint returned: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error testing OAuth endpoint: {e}")
    
    # Test 3: Check client_secrets.json accessibility
    print("\n🔑 Test 3: OAuth Configuration")
    try:
        import json
        from pathlib import Path
        
        secrets_path = Path("client_secrets.json")
        if secrets_path.exists():
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
            
            if 'web' in secrets:
                client_id = secrets['web'].get('client_id', '')
                redirect_uris = secrets['web'].get('redirect_uris', [])
                
                print("✅ client_secrets.json found and valid")
                print(f"🆔 Client ID: {client_id[:20]}...")
                print(f"🔄 Redirect URIs: {len(redirect_uris)} configured")
                
                # Check if current server port is in redirect URIs
                expected_uri = f"{base_url}/auth/google/callback"
                if expected_uri in redirect_uris:
                    print(f"✅ Current server URI is configured: {expected_uri}")
                else:
                    print(f"⚠️ Current server URI not in redirect URIs: {expected_uri}")
                    print("📋 Configured URIs:")
                    for uri in redirect_uris:
                        print(f"   - {uri}")
            else:
                print("❌ Invalid client_secrets.json format (missing 'web' key)")
        else:
            print("❌ client_secrets.json not found")
    except Exception as e:
        print(f"❌ Error checking OAuth configuration: {e}")
    
    # Instructions
    print("\n" + "=" * 60)
    print("📋 Manual Test Instructions:")
    print("1. 🌐 Open browser and go to: http://localhost:5003")
    print("2. 🔐 Click 'Login with Google' button")
    print("3. 👀 Watch the Flask server terminal for log messages:")
    print("   - Look for 'Google OAuth successful'")
    print("   - Look for 'Processing OAuth for email_prefix'")
    print("   - Look for 'Database connection health check passed'")
    print("   - Look for 'User query result'")
    print("   - Look for 'OAuth login successful'")
    print("\n4. 🚨 If you get 'Failed to create user account':")
    print("   - Check Flask terminal for detailed error messages")
    print("   - Look for database constraint violations")
    print("   - Check for duplicate username/email issues")
    
    print("\n💡 Common Issues:")
    print("- 🔄 Duplicate user: User already exists with same email/username")
    print("- 🔌 Database lock: Another process is using the database")
    print("- 🌐 Network: Firewall or antivirus blocking OAuth")
    print("- ⚙️ Configuration: Wrong redirect URI in Google Console")

if __name__ == "__main__":
    test_oauth_flow()