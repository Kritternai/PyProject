#!/usr/bin/env python3
"""
Debug Flask Application Issues
แก้ไขปัญหาและรัน Flask server
"""

import os
import sys
from pathlib import Path

def debug_flask_app():
    print("🔧 Debug Flask Application")
    print("=" * 60)
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    # Add project to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        print("📦 Importing Flask app...")
        from app import create_app
        
        print("🏗️ Creating Flask app...")
        app = create_app()
        
        print("✅ Flask app created successfully")
        
        # Test basic routes
        with app.test_client() as client:
            print("\n🧪 Testing basic routes...")
            
            # Test index route
            try:
                response = client.get('/')
                print(f"   GET / → Status: {response.status_code}")
            except Exception as e:
                print(f"   GET / → Error: {e}")
            
            # Test profile route (should require auth)
            try:
                response = client.get('/partial/profile-view')
                print(f"   GET /partial/profile-view → Status: {response.status_code}")
            except Exception as e:
                print(f"   GET /partial/profile-view → Error: {e}")
        
        print("\n🚀 Starting Flask server...")
        print("📍 URL: http://localhost:5003")
        print("⏹️ Stop: Ctrl+C")
        print("=" * 60)
        
        # Run the server
        app.run(host='0.0.0.0', port=5003, debug=True)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Solutions:")
        print("1. Check if 'app' package exists")
        print("2. Install missing dependencies")
        print("3. Check Python path")
        
    except Exception as e:
        print(f"❌ Flask Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Common Flask issues
        if "address already in use" in str(e).lower():
            print("\n💡 Port 5003 is busy. Try:")
            print("1. Kill existing processes: taskkill /F /IM python.exe")
            print("2. Use different port: app.run(port=5004)")
            
        elif "module" in str(e).lower():
            print("\n💡 Module issues:")
            print("1. Check imports in __init__.py")
            print("2. Verify file paths")
            print("3. Check circular imports")

if __name__ == "__main__":
    debug_flask_app()