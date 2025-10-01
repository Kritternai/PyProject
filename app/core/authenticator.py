from app.core.user_manager import UserManager

class Authenticator:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def login(self, email, password):
        """Login user with email and password"""
        user = self.user_manager.get_user_by_email(email)
        if user and user.check_password(password):
            # Update last login time
            from datetime import datetime
            user.last_login = datetime.utcnow()
            # Use the user_manager to update the user
            self.user_manager.update_user(user.id, new_last_login=datetime.utcnow())
            return user
        return None

    def register(self, email, password, username=None, first_name=None, last_name=None, role='student'):
        """Register new user with enhanced profile information"""
        user = self.user_manager.add_user(
            email=email, 
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        return user
    
    def register_with_profile(self, email, password, profile_data, username=None):
        """Register new user with complete profile data"""
        first_name = profile_data.get('first_name')
        last_name = profile_data.get('last_name')
        role = profile_data.get('role', 'student')
        
        user = self.user_manager.add_user(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        if user and profile_data:
            # Update additional profile information
            self.user_manager.update_user_profile(user.id, profile_data)
            
        return user 