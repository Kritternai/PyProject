#!/usr/bin/env python3
"""
Database Migration: Add Google Credentials Column
Adds google_credentials column to user table for Google Classroom integration
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def add_google_credentials_column():
    """Add google_credentials column to user table"""
    
    # Database path
    db_path = project_root / 'instance' / 'site.db'
    
    if not db_path.exists():
        print("❌ Database not found. Please run the application first.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔧 Adding google_credentials column to user table...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'google_credentials' in columns:
            print("✅ google_credentials column already exists")
            conn.close()
            return True
        
        # Add google_credentials column
        cursor.execute("""
            ALTER TABLE user ADD COLUMN google_credentials TEXT
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added google_credentials column")
        return True
        
    except Exception as e:
        print(f"❌ Error adding google_credentials column: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Main migration function"""
    print("🚀 Google Classroom Integration Migration")
    print("=" * 50)
    
    success = add_google_credentials_column()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Google Classroom integration is now ready.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
