from app.core.user_manager import UserManager

class Authenticator:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def login(self, username, password):
        """Login user with username and password"""
        user = self.user_manager.get_user_by_username(username)
        if user and user.check_password(password):
            # Update last login time
            from datetime import datetime
            user.last_login = datetime.utcnow()
            # Use the user_manager to update the user
            self.user_manager.update_user(user.id, new_last_login=datetime.utcnow())
            return user
        return None

    def register(self, username, email, password, first_name=None, last_name=None, role='student'):
        """Register new user with enhanced profile information"""
        user = self.user_manager.add_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        return user
    
    def register_with_profile(self, username, email, password, profile_data):
        """Register new user with complete profile data"""
        first_name = profile_data.get('first_name')
        last_name = profile_data.get('last_name')
        role = profile_data.get('role', 'student')
        
        user = self.user_manager.add_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        if user and profile_data:
            # Update additional profile information
            self.user_manager.update_user_profile(user.id, profile_data)
            
        return user 