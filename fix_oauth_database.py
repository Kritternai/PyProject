#!/usr/bin/env python3
"""
Fix OAuth Database Path Issue
เพื่อให้ Google OAuth ใช้ database เดียวกับ Flask app
"""

import os
import sqlite3
import shutil
from pathlib import Path

def print_status(msg):
    print(f"🔧 {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

PROJECT_ROOT = Path(__file__).parent
MAIN_DB = PROJECT_ROOT / "instance" / "site.db"
BACKUP_DB = PROJECT_ROOT / "database" / "instance" / "site.db"

def main():
    print_status("Fixing OAuth Database Path Issue")
    print("=" * 60)
    
    # Check both databases
    main_exists = MAIN_DB.exists()
    backup_exists = BACKUP_DB.exists()
    
    print_status(f"Main DB (x:\\PyProject-1\\instance\\site.db): {'EXISTS' if main_exists else 'NOT FOUND'}")
    print_status(f"Backup DB (x:\\PyProject-1\\database\\instance\\site.db): {'EXISTS' if backup_exists else 'NOT FOUND'}")
    
    if not main_exists and not backup_exists:
        print_error("No database found! Please run database setup first")
        return
    
    # Count users in each database
    main_users = 0
    backup_users = 0
    
    if main_exists:
        try:
            conn = sqlite3.connect(str(MAIN_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user")
            main_users = cursor.fetchone()[0]
            conn.close()
        except Exception as e:
            print_error(f"Failed to read main database: {e}")
    
    if backup_exists:
        try:
            conn = sqlite3.connect(str(BACKUP_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user")
            backup_users = cursor.fetchone()[0]
            conn.close()
        except Exception as e:
            print_error(f"Failed to read backup database: {e}")
    
    print_status(f"Users in main database: {main_users}")
    print_status(f"Users in backup database: {backup_users}")
    
    # Decision logic
    if main_users > 0:
        print_success("Using main database (has users)")
        # Remove backup database to avoid confusion
        if backup_exists:
            print_status("Removing backup database to avoid confusion")
            BACKUP_DB.unlink()
            print_success("Backup database removed")
    elif backup_users > 0:
        print_status("Copying backup database to main location")
        # Ensure main directory exists
        MAIN_DB.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(BACKUP_DB), str(MAIN_DB))
        print_success("Database copied to main location")
        # Remove backup
        BACKUP_DB.unlink()
        print_success("Backup database removed")
    else:
        print_status("Both databases are empty, using main location")
        # Ensure main directory exists
        MAIN_DB.parent.mkdir(parents=True, exist_ok=True)
        if backup_exists and not main_exists:
            shutil.copy2(str(BACKUP_DB), str(MAIN_DB))
            BACKUP_DB.unlink()
            print_success("Empty database moved to main location")
    
    # Verify final state
    print("\n" + "=" * 60)
    print_status("Final Database State:")
    if MAIN_DB.exists():
        conn = sqlite3.connect(str(MAIN_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        # Show recent users
        cursor.execute("SELECT username, email, created_at FROM user ORDER BY created_at DESC LIMIT 3")
        recent_users = cursor.fetchall()
        conn.close()
        
        print_success(f"Main database: {user_count} users")
        if recent_users:
            print_status("Recent users:")
            for username, email, created_at in recent_users:
                print(f"  - {username} ({email}) - {created_at}")
    else:
        print_error("No main database found!")
    
    if BACKUP_DB.exists():
        print_error("Backup database still exists - this might cause confusion")
    else:
        print_success("No backup database - clean state")
    
    print("\n" + "=" * 60)
    print_success("Database path consolidation complete!")
    print_status("Now restart your Flask server to test Google OAuth")

if __name__ == "__main__":
    main()