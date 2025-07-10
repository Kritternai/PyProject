from app.core.user_manager import UserManager

class Authenticator:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def login(self, username, password):
        user = self.user_manager.get_user_by_username(username)
        if user and user.check_password(password):
            return user  # Return the user object if login is successful
        return None  # Return None if login fails

    def register(self, username, email, password):
        user = self.user_manager.add_user(username, email, password)
        return user # Returns User object on success, None on failure (e.g., user exists)
