#!/usr/bin/env python3
"""
Fix Werkzeug Import Issue
แก้ไขปัญหา werkzeug import ใน start_server.py
"""

import os
import sys
import subprocess

def print_status(msg: str) -> None:
    print(f"[INFO] {msg}")

def print_success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")

def print_error(msg: str) -> None:
    print(f"[ERROR] {msg}")

def fix_werkzeug_issue():
    """Fix werkzeug import issue"""
    print_status("Fixing Werkzeug import issue...")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("Running in virtual environment")
    else:
        print_warning("Not in virtual environment, activating...")
        if os.path.exists("venv"):
            if os.name == "nt":
                python_path = os.path.join("venv", "Scripts", "python.exe")
            else:
                python_path = os.path.join("venv", "bin", "python")
            
            if os.path.exists(python_path):
                print_status("Re-executing with virtual environment Python...")
                os.execv(python_path, [python_path] + sys.argv)
            else:
                print_error("Virtual environment Python not found")
                return False
    
    # Install werkzeug
    try:
        print_status("Installing Werkzeug...")
        subprocess.run([sys.executable, "-m", "pip", "install", "werkzeug"], check=True)
        print_success("Werkzeug installed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install Werkzeug: {e}")
        return False
    
    # Test import
    try:
        from werkzeug.security import generate_password_hash
        print_success("Werkzeug import test passed")
        return True
    except ImportError as e:
        print_error(f"Werkzeug import test failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Fix Werkzeug Import Issue")
    print("=" * 60)
    
    if fix_werkzeug_issue():
        print_success("Werkzeug issue fixed successfully!")
        print_status("You can now run start_server.py")
    else:
        print_error("Failed to fix Werkzeug issue")
        print_status("Try running: pip install werkzeug")
        sys.exit(1)

if __name__ == "__main__":
    main()
