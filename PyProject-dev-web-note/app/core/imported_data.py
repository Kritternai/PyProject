from app import db
import datetime
import uuid

class ImportedData(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False) # e.g., 'google_classroom', 'ms_teams'
    data = db.Column(db.JSON, nullable=False) # Store the raw JSON data from the extension
    imported_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<ImportedData {self.platform} for User {self.user_id} at {self.imported_at}>'
