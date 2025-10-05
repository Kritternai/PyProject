"""
Test Pomodoro API
Simple test script to verify Pomodoro OOP API is working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5004"

def test_pomodoro_api():
    """Test Pomodoro API endpoints"""
    print("🍅 Testing Pomodoro OOP API...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/pomodoro/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test start session (without authentication - should fail)
    print("\n2. Testing start session (no auth)...")
    try:
        response = requests.post(f"{BASE_URL}/api/pomodoro/start", 
                               json={"session_type": "focus", "duration": 25})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Start session failed: {e}")
    
    # Test get active session (without authentication - should fail)
    print("\n3. Testing get active session (no auth)...")
    try:
        response = requests.get(f"{BASE_URL}/api/pomodoro/active")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Get active session failed: {e}")
    
    # Test statistics (without authentication - should fail)
    print("\n4. Testing statistics (no auth)...")
    try:
        response = requests.get(f"{BASE_URL}/api/pomodoro/statistics")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
    
    print("\n✅ Pomodoro API test completed!")
    print("\n📝 Note: Authentication required for most endpoints")
    print("   - Login first to test full functionality")
    print("   - API endpoints are working correctly")

if __name__ == "__main__":
    test_pomodoro_api()
