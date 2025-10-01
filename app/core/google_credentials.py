from app import db

class GoogleCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), unique=True, nullable=False)
    token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_uri = db.Column(db.Text, nullable=True)
    client_id = db.Column(db.Text, nullable=False)
    client_secret = db.Column(db.Text, nullable=False)
    scopes = db.Column(db.Text, nullable=False) # Store as comma-separated string or JSON

    def __repr__(self):
        return f'<GoogleCredentials for User {self.user_id}>'
