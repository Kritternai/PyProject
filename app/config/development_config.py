"""
Development Configuration
Settings optimized for local development
"""

import os
import secrets
from .settings import Config


class DevelopmentConfig(Config):
    """Development configuration with debug enabled"""
    
    DEBUG = True
    TESTING = False
    
    # Development secret key (auto-generated)
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
    
    # Database (SQLite for development)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///development.db')
    
    # Session settings for development
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Disable CSRF for easier development
    WTF_CSRF_ENABLED = False
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    
    # Enable template auto-reloading
    TEMPLATES_AUTO_RELOAD = True
    
    # Relaxed security for development
    PREFERRED_URL_SCHEME = 'http'