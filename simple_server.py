#!/usr/bin/env python3
"""
Simple Flask server for testing profile system
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run app
try:
    from app import create_app
    
    app = create_app()
    
    if __name__ == "__main__":
        print("🚀 Starting Simple Flask Server for Profile Testing")
        print("=" * 60)
        print("📍 Server: http://localhost:5003")
        print("👤 Profile: http://localhost:5003 (login first)")
        print("⏹️ Stop: Ctrl+C")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5003)
        
except Exception as e:
    print(f"❌ Error starting Flask app: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Check if all dependencies are installed")
    print("2. Verify database is accessible")
    print("3. Check if port 5003 is available")
    sys.exit(1)