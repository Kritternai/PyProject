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
    
    # Set SQLite database URL
    os.environ['DATABASE_URL'] = 'sqlite:///site.db'
    
    try:
        from app import create_app
        app = create_app('production')
        
        port = int(os.environ.get('PORT', 8000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🌐 Starting server on {host}:{port}")
        print("💾 Using SQLite database")
        app.run(host=host, port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
