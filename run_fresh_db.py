"""
Run this script to:
1. ลบฐานข้อมูลเก่า (instance/site.db)
2. ลบ __pycache__ และ .pyc ทั้งหมด
3. สร้างฐานข้อมูลใหม่
4. สร้าง user ทดสอบ (email=1, password=1)
"""

import os
import shutil
import sqlite3
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

def print_status(msg): print(f"[INFO] {msg}")
def print_success(msg): print(f"[SUCCESS] {msg}")
def print_warning(msg): print(f"[WARNING] {msg}")
def print_error(msg): print(f"[ERROR] {msg}")

def remove_db_and_cache():
    # ลบฐานข้อมูล
    db_path = os.path.join("instance", "site.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print_success("Deleted old database: instance/site.db")
    else:
        print_status("No old database found.")

    # ลบ __pycache__ และ .pyc
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
        for f in files:
            if f.endswith(".pyc"):
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass
    print_success("Cleared all __pycache__ and .pyc files.")

def create_db():
    from database.setup_database import create_complete_database_schema
    create_complete_database_schema()
    print_success("Created new database schema.")

def create_default_user():
    db_path = os.path.join("instance", "site.db")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE email = ?", ("1",))
        if cursor.fetchone():
            print_status("Default test user already exists.")
            conn.close()
            return
        password_hash = generate_password_hash("1")
        user_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO user (id, username, email, password_hash, role, is_active, email_verified, 
                              created_at, updated_at, total_lessons, total_notes, total_tasks) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, "1", "1", password_hash, "student", 1, 0, created_at, created_at, 0, 0, 0))
        conn.commit()
        conn.close()
        print_success("Created default test user: email=1, password=1")
    except Exception as e:
        print_error(f"Failed to create default user: {e}")

def main():
    print_status("=== Resetting database and cache ===")
    remove_db_and_cache()
    print_status("=== Creating new database ===")
    create_db()
    print_status("=== Creating default user ===")
    create_default_user()
    print_success("All done! You can now run your main server script.")

if __name__ == "__main__":
    main()