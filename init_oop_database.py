#!/usr/bin/env python3
"""
Initialize database for OOP architecture
"""

def init_database():
    """Initialize database with proper table creation order"""
    try:
        from app import create_app, db
        from app.infrastructure.di.container import configure_services
        
        print("Creating OOP application...")
        app = create_app()
        configure_services()
        
        with app.app_context():
            print("Creating database tables...")
            
            # Drop all tables first (for clean start)
            db.drop_all()
            print("Dropped all existing tables")
            
            # Create tables in correct order
            db.create_all()
            print("Created all tables successfully")
            
            # Test database connection
            result = db.session.execute(db.text('SELECT 1')).scalar()
            print(f"Database connection test: {result}")
            
        print("✅ Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_database()
