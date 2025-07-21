from app import db
from app.core.user import User
import uuid

class UserManager:
    def add_user(self, username, email, password):
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return None
        user = User(username=username, email=email, password=password)
        user.id = str(uuid.uuid4())
        db.session.add(user)
        db.session.commit()
        return user

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def update_user(self, user_id, new_username=None, new_email=None, new_password=None):
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
        db.session.commit()
        return True

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False 
 