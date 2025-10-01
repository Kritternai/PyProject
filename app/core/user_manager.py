from app import db
from app.core.user import User
import uuid

class UserManager:
    def add_user(self, username, email, password, first_name=None, last_name=None, role='student'):
        """Add a new user with enhanced profile information"""
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return None
        
        user = User(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # ID is automatically generated in the model
        db.session.add(user)
        db.session.commit()
        return user

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def update_user(self, user_id, new_username=None, new_email=None, new_password=None, 
                   new_first_name=None, new_last_name=None, new_role=None, new_bio=None,
                   new_last_login=None):
        """Update user information with enhanced profile fields"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        if new_username and new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                return False
            user.username = new_username
            
        if new_email and new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                return False
            user.email = new_email
            
        if new_password:
            user.set_password(new_password)
            
        if new_first_name is not None:
            user.first_name = new_first_name
            
        if new_last_name is not None:
            user.last_name = new_last_name
            
        if new_role is not None:
            user.role = new_role
            
        if new_bio is not None:
            user.bio = new_bio
            
        if new_last_login is not None:
            user.last_login = new_last_login
            
        db.session.commit()
        return True

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        # Update profile fields
        if 'first_name' in profile_data:
            user.first_name = profile_data['first_name']
        if 'last_name' in profile_data:
            user.last_name = profile_data['last_name']
        if 'bio' in profile_data:
            user.bio = profile_data['bio']
        if 'role' in profile_data:
            user.role = profile_data['role']
        if 'preferences' in profile_data:
            user.preferences = profile_data['preferences']
            
        db.session.commit()
        return True
    
    def update_user_statistics(self, user_id, stats_data):
        """Update user statistics"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        if 'total_lessons' in stats_data:
            user.total_lessons = stats_data['total_lessons']
        if 'total_notes' in stats_data:
            user.total_notes = stats_data['total_notes']
        if 'total_tasks' in stats_data:
            user.total_tasks = stats_data['total_tasks']
            
        db.session.commit()
        return True
    
    def get_all_users(self, role=None, is_active=None):
        """Get users with optional filtering"""
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
            
        return query.all()
    
    def search_users(self, search_term, limit=20):
        """Search users by username, email, or name"""
        search_pattern = f'%{search_term}%'
        
        return User.query.filter(
            db.or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            )
        ).limit(limit).all() 