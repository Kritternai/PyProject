#!/usr/bin/env python3
"""
Quick Web Test
ทดสอบการเข้าถึงเว็บแบบง่าย
"""

import requests
import time

def test_website():
    print("🌐 Testing Website Access")
    print("=" * 50)
    
    url = "http://localhost:5003"
    
    print(f"🔗 Testing: {url}")
    
    for attempt in range(3):
        try:
            print(f"   Attempt {attempt + 1}/3...")
            response = requests.get(url, timeout=5)
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📏 Content Length: {len(response.text)} chars")
            
            if response.status_code == 200:
                print("   🎉 Website is accessible!")
                
                # Check if it's the expected page
                if "Smart Learning Hub" in response.text or "enchat" in response.text:
                    print("   ✅ Correct page loaded")
                else:
                    print("   ⚠️ Unexpected page content")
                    
                return True
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection refused (attempt {attempt + 1})")
            if attempt < 2:
                print("   ⏳ Waiting 2 seconds...")
                time.sleep(2)
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout (attempt {attempt + 1})")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n💡 Troubleshooting:")
    print("1. Check if Flask server is running")
    print("2. Try opening: http://localhost:5003 in browser")
    print("3. Check terminal running Flask for errors")
    return False

if __name__ == "__main__":
    test_website()