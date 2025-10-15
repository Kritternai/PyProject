#!/usr/bin/env python3
"""
SQLite start script for Render deployment
This script uses SQLite instead of PostgreSQL to avoid psycopg2 issues
"""

import os
import sys

def main():
    """Main function"""
    print("🚀 Starting Smart Learning Hub with SQLite...")
    
    # Debug Python environment
    print(f"🐍 Python version: {sys.version}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🐍 Current working directory: {os.getcwd()}")
    
    # Check if Flask is available
    try:
        import flask
        print(f"✅ Flask version: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        print("📦 Available packages:")
        import subprocess
        try:
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
            print(result.stdout)
        except:
            print("Could not list packages")
        sys.exit(1)
    
    # Set SQLite database URL
    os.environ['DATABASE_URL'] = 'sqlite:///site.db'
    
    try:
        print("📦 Importing application...")
        from app import create_app
        print("✅ Application imported successfully")
        
        print("🏗️ Creating application instance...")
        app = create_app('production')
        print("✅ Application instance created")
        
        port = int(os.environ.get('PORT', 8000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🌐 Starting server on {host}:{port}")
        print("💾 Using SQLite database")
        app.run(host=host, port=port, debug=False)
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("🔍 Python path:")
        for path in sys.path:
            print(f"  - {path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
