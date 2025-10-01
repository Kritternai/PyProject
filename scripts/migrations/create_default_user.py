#!/usr/bin/env python
"""
Create default test user for development.
Email: 1
Password: 1
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db
from app.core.user_manager import UserManager
from app.core.authenticator import Authenticator

def create_default_user():
    """Create default test user."""
    app = create_app()
    
    with app.app_context():
        user_manager = UserManager()
        authenticator = Authenticator(user_manager)
        
        # Check if default user already exists
        existing_user = user_manager.get_user_by_email('1')
        
        if existing_user:
            print(f"✓ Default user already exists:")
            print(f"  Email: 1")
            print(f"  Username: {existing_user.username}")
            print(f"  ID: {existing_user.id}")
            
            # Test password
            if existing_user.check_password('1'):
                print(f"  Password: ✓ Verified")
            else:
                print(f"  Password: ✗ Invalid - Updating...")
                existing_user.set_password('1')
                db.session.commit()
                print(f"  Password: ✓ Updated")
        else:
            print("Creating default test user...")
            try:
                user = authenticator.register('1', '1')
                if user:
                    print(f"✓ Default user created successfully:")
                    print(f"  Email: 1")
                    print(f"  Password: 1")
                    print(f"  Username: {user.username}")
                    print(f"  ID: {user.id}")
                else:
                    print("✗ Failed to create default user")
                    return False
            except Exception as e:
                print(f"✗ Error creating user: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return True

if __name__ == '__main__':
    success = create_default_user()
    sys.exit(0 if success else 1)

