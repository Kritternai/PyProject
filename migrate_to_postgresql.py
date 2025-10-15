#!/usr/bin/env python3
"""
Migration script from SQLite to PostgreSQL
This script will help migrate your existing SQLite data to PostgreSQL
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import sys

def get_sqlite_data(db_path):
    """Extract data from SQLite database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    data = {}
    for table in tables:
        if table == 'sqlite_sequence':
            continue
            
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        data[table] = [dict(row) for row in rows]
    
    conn.close()
    return data

def get_postgresql_connection(database_url):
    """Connect to PostgreSQL database"""
    parsed_url = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=parsed_url.hostname,
        port=parsed_url.port,
        database=parsed_url.path[1:],  # Remove leading slash
        user=parsed_url.username,
        password=parsed_url.password
    )
    return conn

def create_tables_postgresql(conn):
    """Create tables in PostgreSQL using Flask-SQLAlchemy"""
    print("📊 Creating PostgreSQL tables...")
    
    # Import Flask app and create tables
    from app import create_app, db
    
    app = create_app('production')
    with app.app_context():
        db.create_all()
        print("✅ PostgreSQL tables created successfully")

def migrate_data(data, conn):
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Migrating data to PostgreSQL...")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Define table order (respecting foreign key constraints)
    table_order = [
        'user',
        'lesson', 
        'lesson_section',
        'note',
        'task',
        'announcement',
        'assignment',
        'member',
        'note_file',
        'pomodoro_session',
        'pomodoro_statistics',
        'classwork_task',
        'classwork_material',
        'classwork_note',
        'classwork_session',
        'classwork_progress',
        'grade_config',
        'grade_category',
        'grade_item',
        'grade_entry',
        'grade_summary',
        'stream_post',
        'stream_comment',
        'stream_attachment'
    ]
    
    for table_name in table_order:
        if table_name in data and data[table_name]:
            print(f"  📝 Migrating {table_name} ({len(data[table_name])} rows)...")
            
            # Get column names
            columns = list(data[table_name][0].keys())
            
            # Create INSERT query
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Insert data
            for row in data[table_name]:
                values = [row.get(col) for col in columns]
                try:
                    cursor.execute(insert_query, values)
                except Exception as e:
                    print(f"    ⚠️  Warning: Failed to insert row in {table_name}: {e}")
                    continue
            
            conn.commit()
            print(f"  ✅ {table_name} migrated successfully")
    
    cursor.close()

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to PostgreSQL migration...")
    
    # Check if SQLite database exists
    sqlite_path = "instance/site.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found at {sqlite_path}")
        print("💡 Make sure you have an existing SQLite database to migrate from")
        return
    
    # Get PostgreSQL connection string
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("💡 Set DATABASE_URL to your PostgreSQL connection string")
        return
    
    try:
        # Extract SQLite data
        print("📖 Reading SQLite data...")
        data = get_sqlite_data(sqlite_path)
        print(f"✅ Found {len(data)} tables with data")
        
        # Connect to PostgreSQL
        print("🔗 Connecting to PostgreSQL...")
        pg_conn = get_postgresql_connection(database_url)
        print("✅ Connected to PostgreSQL")
        
        # Create tables
        create_tables_postgresql(pg_conn)
        
        # Migrate data
        migrate_data(data, pg_conn)
        
        # Close connection
        pg_conn.close()
        
        print("🎉 Migration completed successfully!")
        print("💡 Your data is now in PostgreSQL and ready for Render deployment")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
