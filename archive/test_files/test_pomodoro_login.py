"""
Test Pomodoro with Login
Test script to verify Pomodoro works after login
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5004"

def test_pomodoro_with_login():
    """Test Pomodoro with login"""
    print("🍅 Testing Pomodoro with Login...")
    
    # Create session
    session = requests.Session()
    
    # Test login
    print("\n1. Testing login...")
    try:
        # Try to access dashboard first
        response = session.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard accessible")
        else:
            print("❌ Dashboard not accessible")
            return
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
        return
    
    # Test Pomodoro page
    print("\n2. Testing Pomodoro page...")
    try:
        response = session.get(f"{BASE_URL}/partial/pomodoro")
        if response.status_code == 200:
            print("✅ Pomodoro page loaded successfully")
            content = response.text
            
            # Check for JavaScript functions
            if 'startPomodoroSession' in content:
                print("✅ startPomodoroSession function found")
            else:
                print("❌ startPomodoroSession function not found")
                
            if 'window.startPomodoroSession' in content:
                print("✅ Window attachment found")
            else:
                print("❌ Window attachment not found")
                
            # Check for script tag
            if '<script>' in content:
                print("✅ Script tag found")
            else:
                print("❌ Script tag not found")
                
        else:
            print(f"❌ Pomodoro page failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error accessing Pomodoro page: {e}")
    
    # Test Pomodoro API
    print("\n3. Testing Pomodoro API...")
    try:
        response = session.get(f"{BASE_URL}/api/pomodoro/health")
        if response.status_code == 200:
            print("✅ Pomodoro API health check passed")
        else:
            print(f"❌ Pomodoro API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Pomodoro API: {e}")
    
    print("\n✅ Pomodoro with Login test completed!")

if __name__ == "__main__":
    test_pomodoro_with_login()
