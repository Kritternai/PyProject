#!/usr/bin/env python3
"""
Script to fix route decorators in routes.py
"""

import re

def fix_routes():
    """Fix route decorators in routes.py"""
    file_path = "app/routes.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace @app.route with @main_bp.route
        content = re.sub(r'@app\.route', '@main_bp.route', content)
        content = re.sub(r'@app\.before_request', '@main_bp.before_request', content)
        content = re.sub(r'@app\.after_request', '@main_bp.after_request', content)
        content = re.sub(r'@app\.errorhandler', '@main_bp.errorhandler', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed route decorators in routes.py")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing routes: {e}")
        return False

if __name__ == "__main__":
    fix_routes()
