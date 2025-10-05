"""
Test script for rate limiting functionality.
Tests DoS protection for note management endpoints.
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def test_rate_limiting():
    """Test rate limiting functionality."""
    base_url = "http://localhost:5000"
    
    # Test data
    test_user_data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    
    note_data = {
        'title': 'Test Note',
        'content': 'This is a test note for rate limiting'
    }
    
    print("🔒 Testing Rate Limiting for Note Management System")
    print("=" * 60)
    
    # Create session
    session = requests.Session()
    
    try:
        # Login first (if needed)
        print("1. Attempting to login...")
        login_response = session.post(f"{base_url}/api/auth/login", data=test_user_data)
        if login_response.status_code == 200:
            print("✅ Login successful")
        else:
            print("⚠️  Login failed, continuing with anonymous requests")
        
        # Test 1: Normal rate limiting
        print("\n2. Testing normal rate limiting (10 requests/5 seconds)...")
        success_count = 0
        rate_limited_count = 0
        
        for i in range(15):  # Try 15 requests (should hit limit)
            response = session.post(f"{base_url}/partial/note/add", data=note_data)
            
            if response.status_code == 200 or response.status_code == 201:
                success_count += 1
                print(f"   Request {i+1}: ✅ Success")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"   Request {i+1}: 🚫 Rate limited")
                try:
                    error_data = response.json()
                    print(f"      Message: {error_data.get('message', 'Rate limit exceeded')}")
                except:
                    pass
            else:
                print(f"   Request {i+1}: ❓ Other status: {response.status_code}")
            
            time.sleep(0.2)  # Small delay between requests
        
        print(f"\n   Results: {success_count} successful, {rate_limited_count} rate limited")
        
        # Test 2: Wait and retry
        print("\n3. Waiting 6 seconds for rate limit reset...")
        time.sleep(6)
        
        print("4. Testing after rate limit reset...")
        response = session.post(f"{base_url}/partial/note/add", data=note_data)
        if response.status_code in [200, 201]:
            print("   ✅ Request successful after reset")
        elif response.status_code == 429:
            print("   🚫 Still rate limited")
        else:
            print(f"   ❓ Status: {response.status_code}")
        
        # Test 3: Concurrent requests (stress test)
        print("\n5. Testing concurrent requests (stress test)...")
        
        def make_request(session, url, data, request_id):
            try:
                response = session.post(url, data=data)
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'rate_limited': response.status_code == 429
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Create multiple sessions for concurrent testing
        sessions = [requests.Session() for _ in range(5)]
        
        # Login all sessions
        for sess in sessions:
            try:
                sess.post(f"{base_url}/api/auth/login", data=test_user_data)
            except:
                pass
        
        # Make concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(25):  # 25 concurrent requests
                session_to_use = sessions[i % len(sessions)]
                future = executor.submit(
                    make_request, 
                    session_to_use, 
                    f"{base_url}/partial/note/add", 
                    note_data, 
                    i+1
                )
                futures.append(future)
            
            concurrent_success = 0
            concurrent_rate_limited = 0
            concurrent_errors = 0
            
            for future in as_completed(futures):
                result = future.result()
                if result['status'] in [200, 201]:
                    concurrent_success += 1
                elif result['status'] == 429:
                    concurrent_rate_limited += 1
                else:
                    concurrent_errors += 1
        
        print(f"   Concurrent results: {concurrent_success} successful, {concurrent_rate_limited} rate limited, {concurrent_errors} errors")
        
        # Test 4: IP-based rate limiting
        print("\n6. Testing IP-based rate limiting...")
        # This would require multiple IP addresses to test properly
        print("   (IP-based testing requires multiple IP addresses)")
        
        print("\n" + "=" * 60)
        print("🎯 Rate Limiting Test Summary:")
        print(f"   - Normal requests: {success_count}/{success_count + rate_limited_count} allowed")
        print(f"   - Rate limited: {rate_limited_count} requests blocked")
        print(f"   - Concurrent: {concurrent_success} successful, {concurrent_rate_limited} blocked")
        
        if rate_limited_count > 0:
            print("   ✅ Rate limiting is working correctly!")
        else:
            print("   ⚠️  Rate limiting may not be working as expected")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        session.close()


if __name__ == "__main__":
    print("Starting rate limiting tests...")
    print("Make sure your Flask app is running on http://localhost:5000")
    print()
    
    try:
        test_rate_limiting()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
