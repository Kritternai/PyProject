#!/usr/bin/env python3
"""
Test website functionality
"""
import requests
import sys

def test_website():
    print('🌐 TESTING WEBSITE FUNCTIONALITY')
    print('=' * 50)
    
    base_urls = [
        'http://localhost:5003',
        'http://127.0.0.1:5003'
    ]
    
    test_pages = [
        ('/', 'Main page'),
        ('/login', 'Login page'),
        ('/register', 'Register page'),
        ('/dashboard', 'Dashboard (requires login)'),
        ('/auth/google/login', 'Google OAuth (should redirect)')
    ]
    
    for base_url in base_urls:
        print(f'\n🔍 Testing: {base_url}')
        print('-' * 30)
        
        for path, description in test_pages:
            url = f'{base_url}{path}'
            try:
                response = requests.get(url, timeout=10, allow_redirects=False)
                status = response.status_code
                
                if status == 200:
                    print(f'✅ {description}: OK ({status})')
                elif status in [302, 301]:
                    location = response.headers.get('Location', 'No location')
                    print(f'🔄 {description}: Redirect ({status}) -> {location}')
                elif status == 404:
                    print(f'❌ {description}: Not Found ({status})')
                elif status == 500:
                    print(f'💥 {description}: Server Error ({status})')
                else:
                    print(f'⚠️ {description}: Unexpected ({status})')
                    
            except requests.exceptions.ConnectionError:
                print(f'🔌 {description}: Connection refused - Server not running?')
                break
            except requests.exceptions.Timeout:
                print(f'⏰ {description}: Timeout - Server slow?')
            except Exception as e:
                print(f'❌ {description}: Error - {str(e)}')
        
        # Test if at least main page works
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                print(f'\n🎉 {base_url} is WORKING!')
                return True
        except:
            continue
    
    print('\n💥 Website appears to be DOWN or unreachable!')
    return False

def check_common_issues():
    print('\n🔧 COMMON ISSUES TO CHECK:')
    print('=' * 50)
    
    # Check if port is in use
    import socket
    for port in [5003, 5004]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f'✅ Port {port}: In use (server likely running)')
            else:
                print(f'❌ Port {port}: Not in use')
        except Exception as e:
            print(f'⚠️ Port {port}: Check failed - {e}')
    
    # Check if Flask process is running
    import psutil
    flask_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'python' in cmdline.lower() and ('flask' in cmdline.lower() or 'start_server' in cmdline.lower()):
                    flask_processes.append(proc.info)
        except:
            continue
    
    if flask_processes:
        print(f'✅ Flask processes found: {len(flask_processes)}')
    else:
        print('❌ No Flask processes found')
    
    print('\n📋 TROUBLESHOOTING STEPS:')
    print('1. Make sure Flask server is running (check terminal output above)')
    print('2. Try accessing: http://localhost:5003')
    print('3. Check browser console for JavaScript errors')
    print('4. Check Flask server logs for error messages')
    print('5. Try different browser or incognito mode')

if __name__ == "__main__":
    website_working = test_website()
    check_common_issues()
    
    if website_working:
        print('\n🎉 CONCLUSION: Website appears to be working!')
        print('If you still have issues, check:')
        print('- Browser cache/cookies')
        print('- Firewall/antivirus blocking')
        print('- Network connectivity')
    else:
        print('\n💥 CONCLUSION: Website has issues!')
        print('Please start the Flask server and try again.')