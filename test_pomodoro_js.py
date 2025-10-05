"""
Test Pomodoro JavaScript Functions
Test script to verify Pomodoro JavaScript functions are working
"""
import requests
import re

BASE_URL = "http://127.0.0.1:5004"

def test_pomodoro_js():
    """Test Pomodoro JavaScript functions"""
    print("🍅 Testing Pomodoro JavaScript Functions...")
    
    # Create session
    session = requests.Session()
    
    # Test login first
    print("\n1. Testing login...")
    try:
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
            content = response.text
            
            # Check for JavaScript functions
            functions = [
                'startPomodoroSession',
                'pausePomodoroSession', 
                'resumePomodoroSession',
                'completePomodoroSession',
                'cancelPomodoroSession',
                'getPomodoroStatistics',
                'getProductivityInsights',
                'getUserSessions'
            ]
            
            for func in functions:
                if func in content:
                    print(f"✅ Function {func} found")
                else:
                    print(f"❌ Function {func} not found")
            
            # Check for window attachment
            if 'window.startPomodoroSession' in content:
                print("✅ Window attachment found")
            else:
                print("❌ Window attachment not found")
                
        else:
            print(f"❌ Pomodoro page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Pomodoro page: {e}")
    
    print("\n✅ Pomodoro JavaScript test completed!")

if __name__ == "__main__":
    test_pomodoro_js()
