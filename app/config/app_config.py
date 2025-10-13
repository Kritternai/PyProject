import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 5003))
    
    # Database Configuration
    # Create absolute path to database file
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
    DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'site.db')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
