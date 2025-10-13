#!/usr/bin/env python3
"""
สคริปต์ตรวจสอบและแก้ไขปัญหาเซิร์ฟเวอร์เว็บ
Web server troubleshooting and fix script
"""

import subprocess
import time
import requests
import socket
from datetime import datetime

def check_port_availability(port):
    """ตรวจสอบว่าพอร์ตว่างหรือไม่"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # True if port is available
    except:
        return True

def find_flask_processes():
    """ค้นหาโปรเซส Flask ที่กำลังรันอยู่"""
    try:
        # Windows netstat command
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        flask_ports = []
        for line in lines:
            if ':500' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[1]
                    if ':' in addr:
                        port = addr.split(':')[-1]
                        if port.isdigit():
                            flask_ports.append(int(port))
        
        return flask_ports
    except Exception as e:
        print(f"Error finding Flask processes: {e}")
        return []

def test_website_connectivity():
    """ทดสอบการเชื่อมต่อเว็บไซต์"""
    
    print("🌐 Testing Website Connectivity")
    print("=" * 50)
    
    # ทดสอบพอร์ตต่างๆ
    test_ports = [5000, 5003, 5004, 8000]
    working_ports = []
    
    for port in test_ports:
        print(f"🔍 Testing port {port}...")
        
        # ตรวจสอบ socket connection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Port {port} is listening")
                
                # ทดสอบ HTTP request
                try:
                    response = requests.get(f'http://localhost:{port}', timeout=5)
                    print(f"   ✅ HTTP {response.status_code}: {response.reason}")
                    working_ports.append(port)
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ HTTP error: {e}")
            else:
                print(f"   ❌ Port {port} not available")
                
        except Exception as e:
            print(f"   ❌ Socket error: {e}")
    
    return working_ports

def start_flask_server():
    """เริ่มเซิร์ฟเวอร์ Flask"""
    
    print("\n🚀 Starting Flask Server")
    print("=" * 50)
    
    # ตรวจสอบไฟล์ start_server.py
    import os
    if not os.path.exists('start_server.py'):
        print("❌ start_server.py not found")
        return False
    
    print("✅ start_server.py found")
    
    # หา port ที่ว่าง
    available_port = None
    for port in [5003, 5004, 5000, 8000]:
        if check_port_availability(port):
            available_port = port
            break
    
    if not available_port:
        print("❌ No available ports found")
        return False
    
    print(f"✅ Using port {available_port}")
    
    try:
        # เริ่มเซิร์ฟเวอร์
        print("🔄 Starting server...")
        cmd = ['python', 'start_server.py']
        
        # เริ่มในโหมด background
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # รอสักครู่ให้เซิร์ฟเวอร์เริ่มต้น
        time.sleep(3)
        
        # ตรวจสอบว่าเซิร์ฟเวอร์เริ่มแล้วหรือยัง
        if process.poll() is None:
            print("✅ Server process started")
            
            # ทดสอบการเชื่อมต่อ
            for attempt in range(5):
                try:
                    response = requests.get(f'http://localhost:{available_port}', timeout=2)
                    print(f"✅ Server responding on http://localhost:{available_port}")
                    return True
                except:
                    print(f"⏳ Waiting for server (attempt {attempt + 1}/5)...")
                    time.sleep(2)
            
            print("❌ Server not responding after 10 seconds")
            return False
        else:
            print("❌ Server process failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    
    print("🔧 Web Server Troubleshooting")
    print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # ค้นหาโปรเซส Flask ที่มีอยู่
    flask_ports = find_flask_processes()
    if flask_ports:
        print(f"🔍 Found Flask processes on ports: {flask_ports}")
    else:
        print("🔍 No Flask processes found")
    
    # ทดสอบการเชื่อมต่อ
    working_ports = test_website_connectivity()
    
    if working_ports:
        print(f"\n✅ Website is working on ports: {working_ports}")
        for port in working_ports:
            print(f"   🌐 http://localhost:{port}")
    else:
        print("\n❌ No working website found")
        print("🔄 Attempting to start server...")
        
        if start_flask_server():
            print("✅ Server started successfully!")
        else:
            print("❌ Failed to start server")
            print("\n🛠️  Manual steps to try:")
            print("1. cd x:\\PyProject-1")
            print("2. python start_server.py")
            print("3. Open browser to http://localhost:5003 or http://localhost:5004")

if __name__ == "__main__":
    main()