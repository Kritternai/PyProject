#!/usr/bin/env python3
"""
Test register functionality fix
"""

import requests
import json

def test_register():
    """Test register endpoint"""
    url = "http://127.0.0.1:5003/partial/register"
    
    # Test data
    data = {
        'username': 'testuser123',
        'email': 'test123@example.com',
        'password': 'TestPass123!'
    }
    
    try:
        print("Testing register endpoint...")
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            if result.get('redirect'):
                print(f"Redirect: {result.get('redirect')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_login():
    """Test login endpoint"""
    url = "http://127.0.0.1:5003/partial/login"
    
    # Test data
    data = {
        'email': 'test123@example.com',
        'password': 'TestPass123!'
    }
    
    try:
        print("\nTesting login endpoint...")
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            if result.get('redirect'):
                print(f"Redirect: {result.get('redirect')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
    test_login()
