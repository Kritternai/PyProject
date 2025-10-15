#!/usr/bin/env python3
"""
Development server runner with basic configuration
"""
import os
import secrets
from app import create_app

def main():
    # Set environment to development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['CONFIG_TYPE'] = 'development'
    
    # Set basic environment variables for development
    if not os.environ.get('FLASK_SECRET_KEY'):
        os.environ['FLASK_SECRET_KEY'] = secrets.token_hex(32)
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///development.db'
    
    # Create and run the app
    app = create_app()
    
    print("🚀 Starting Smart Learning Hub (Development Mode)")
    print("📍 Server: http://localhost:8001")
    print("🔧 Environment: Development")
    print("💾 Database: SQLite")
    print("🎨 Forgot Password: http://localhost:8001/forgot_password")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=8001,
        debug=True,
        use_reloader=True
    )

if __name__ == '__main__':
    main()