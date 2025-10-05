"""
Test Pomodoro Frontend
Test script to verify Pomodoro frontend is working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5004"

def test_pomodoro_frontend():
    """Test Pomodoro frontend functionality"""
    print("🍅 Testing Pomodoro Frontend...")
    
    # Create session
    session = requests.Session()
    
    # Test login first
    print("\n1. Testing login...")
    try:
        # Try to access dashboard to see if we need to login
        response = session.get(f"{BASE_URL}/")
        if "login" in response.url:
            print("❌ Need to login first")
            return
        else:
            print("✅ Already logged in or no login required")
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
        return
    
    # Test Pomodoro page
    print("\n2. Testing Pomodoro page...")
    try:
        response = session.get(f"{BASE_URL}/partial/pomodoro")
        if response.status_code == 200:
            print("✅ Pomodoro page loaded successfully")
            # Check if it contains expected elements
            content = response.text
            if "pomodoro" in content.lower():
                print("✅ Pomodoro content found")
            if "start" in content.lower():
                print("✅ Start button found")
            if "timer" in content.lower():
                print("✅ Timer elements found")
        else:
            print(f"❌ Pomodoro page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Pomodoro page: {e}")
    
    # Test Pomodoro API
    print("\n3. Testing Pomodoro API...")
    try:
        # Test health check
        response = session.get(f"{BASE_URL}/api/pomodoro/health")
        if response.status_code == 200:
            print("✅ Pomodoro API health check passed")
        else:
            print(f"❌ Pomodoro API health check failed: {response.status_code}")
        
        # Test start session
        response = session.post(f"{BASE_URL}/api/pomodoro/start", 
                               json={"session_type": "focus", "duration": 25})
        if response.status_code == 201:
            print("✅ Start session API working")
            session_data = response.json()
            print(f"   Session ID: {session_data.get('session', {}).get('id', 'N/A')}")
        else:
            print(f"❌ Start session failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error testing Pomodoro API: {e}")
    
    print("\n✅ Pomodoro Frontend test completed!")

if __name__ == "__main__":
    test_pomodoro_frontend()
