#!/usr/bin/env python3
"""
Debug registration functionality
"""

def test_registration():
    """Test registration step by step"""
    try:
        print("1. Creating app...")
        from app import create_app, db
        from app.infrastructure.di.container import configure_services
        
        app = create_app()
        configure_services()
        
        print("2. Testing user service...")
        with app.app_context():
            from app.infrastructure.di.container import get_service
            from app.domain.interfaces.services.user_service import UserService
            
            user_service = get_service(UserService)
            print(f"User service: {user_service}")
            
            print("3. Testing registration...")
            try:
                user_service.register_user("testuser2", "test2@example.com", "TestPass123!")
                print("✅ Registration successful!")
            except Exception as e:
                print(f"❌ Registration failed: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()
