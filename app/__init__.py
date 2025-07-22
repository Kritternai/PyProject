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

# Import models so SQLAlchemy knows about them
from app.core.user import User
from app.core.lesson import Lesson
from app.core.imported_data import ImportedData
from app.core.google_credentials import GoogleCredentials # Import GoogleCredentials model
from app.core.course_linkage import CourseLinkage # Import CourseLinkage model

from app import routes