"""
Production Configuration
Enhanced security and performance settings for production deployment
"""

import os
from .settings import Config


class ProductionConfig(Config):
    """Production configuration with enhanced security"""
    
    DEBUG = False
    TESTING = False
    
    # Enhanced security settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'your_strong_random_flask_secret_key':
        raise ValueError("FLASK_SECRET_KEY must be set with a secure value in production")
    
    # Database settings - prefer PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Security headers
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'uploads')
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 8000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Disable insecure transport for production
    OAUTHLIB_INSECURE_TRANSPORT = False
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    # Redis configuration (if available)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Email configuration (if available)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    @classmethod
    def validate_config(cls):
        """Validate production configuration"""
        required_vars = [
            'FLASK_SECRET_KEY',
            'GOOGLE_CLIENT_ID', 
            'GOOGLE_CLIENT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate secret key strength
        secret_key = os.environ.get('FLASK_SECRET_KEY', '')
        if len(secret_key) < 32:
            raise ValueError("FLASK_SECRET_KEY must be at least 32 characters long")
        
        return True
