#!/usr/bin/env python3
"""
Simple test script to check if note editor route is accessible
Run this to verify the server and route are working
"""

import requests
import sys

def test_note_editor_route():
    base_url = "http://localhost:5004"
    
    print("🔍 Testing Note Editor Route...")
    print(f"Base URL: {base_url}")
    
    try:
        # Test the partial note editor route
        url = f"{base_url}/partial/note/editor"
        print(f"\n📡 Testing: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Check if our script tag is in the response
            if '<script>' in response.text and 'Note editor fragment script loaded' in response.text:
                print("✅ Script tag found in response!")
            else:
                print("❌ Script tag NOT found in response")
                
            # Check if toolbar is in the response
            if 'editorToolbar' in response.text:
                print("✅ Toolbar found in response!")
            else:
                print("❌ Toolbar NOT found in response")
                
            # Save response to file for inspection
            with open('note_editor_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Response saved to: note_editor_response.html")
            
        elif response.status_code == 401:
            print("🔐 Authentication required - you need to login first")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on localhost:5000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_note_editor_route()
