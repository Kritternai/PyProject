#!/usr/bin/env python3
"""
Alternative start script for Render deployment
This script ensures all dependencies are available before starting
"""

import os
import sys

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'flask',
        'flask_sqlalchemy', 
        'flask_migrate',
        'gunicorn',
        'psycopg2'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Installing missing dependencies...")
        os.system(f"pip install {' '.join(missing)}")
    
    return len(missing) == 0

def main():
    """Main function"""
    print("🚀 Starting Smart Learning Hub for Render...")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Import and start the app
    try:
        from app import create_app
        app = create_app('production')
        
        port = int(os.environ.get('PORT', 8000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🌐 Starting server on {host}:{port}")
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
