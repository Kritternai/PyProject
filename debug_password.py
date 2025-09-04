#!/usr/bin/env python3
"""
Debug password functionality
"""

def test_password():
    """Test password step by step"""
    try:
        print("1. Creating app...")
        from app import create_app, db
        from app.infrastructure.di.container import configure_services
        
        app = create_app()
        configure_services()
        
        print("2. Testing password...")
        with app.app_context():
            from app.infrastructure.di.container import get_service
            from app.domain.interfaces.services.user_service import UserService
            from app.domain.value_objects.password import Password
            
            user_service = get_service(UserService)
            
            # Test password creation
            password = Password("TestPass123!")
            print(f"Password hash: {password.value}")
            print(f"Is hashed: {password._is_hashed}")
            
            # Test password check
            result = password.check_password("TestPass123!")
            print(f"Password check result: {result}")
            
            # Test with wrong password
            result2 = password.check_password("WrongPassword")
            print(f"Wrong password check result: {result2}")
            
            # Get user from database
            from app.infrastructure.di.container import get_service
            from app.domain.interfaces.repositories.user_repository import UserRepository
            from app.domain.value_objects.email import Email
            
            user_repo = get_service(UserRepository)
            email = Email("test2@example.com")
            user = user_repo.get_by_email(email)
            
            if user:
                print(f"User found: {user.username}")
                print(f"User password hash: {user.password.value}")
                print(f"User password is_hashed: {user.password._is_hashed}")
                
                # Test user password
                result3 = user.password.check_password("TestPass123!")
                print(f"User password check result: {result3}")
            else:
                print("User not found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_password()
