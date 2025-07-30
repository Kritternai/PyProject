from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_fallback_secret_key') # Use environment variable for secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

db = SQLAlchemy(app)

# Custom template filters
@app.template_filter('lesson_color_primary')
def lesson_color_primary(color_id):
    colors = {
        1: '#007bff',
        2: '#28a745', 
        3: '#dc3545',
        4: '#ffc107',
        5: '#6f42c1',
        6: '#fd7e14'
    }
    return colors.get(int(color_id), '#007bff')

@app.template_filter('lesson_color_secondary')
def lesson_color_secondary(color_id):
    colors = {
        1: '#0056b3',
        2: '#1e7e34',
        3: '#c82333', 
        4: '#e0a800',
        5: '#5a2d91',
        6: '#e8690b'
    }
    return colors.get(int(color_id), '#0056b3')

@app.template_filter('from_json')
def from_json(value):
    import json
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

@app.template_filter('to_json')
def to_json(value):
    import json
    if value is None:
        return '[]'
    if value:
        try:
            return json.dumps(value)
        except:
            return '[]'
    return '[]'

# Import models so SQLAlchemy knows about them
from app.core.user import User
from app.core.lesson import Lesson
from app.core.note import Note
from app.core.files import Files
from app.core.imported_data import ImportedData
from app.core.google_credentials import GoogleCredentials # Import GoogleCredentials model
from app.core.course_linkage import CourseLinkage # Import CourseLinkage model

from app import routes