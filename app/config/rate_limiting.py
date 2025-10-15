"""
Rate Limiting Configuration for Smart Learning Hub
Provides rate limiting for API endpoints and authentication
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

def init_rate_limiter(app):
    """Initialize Flask-Limiter with the Flask app"""
    
    # Initialize limiter with app
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["1000 per hour", "100 per minute"],
        storage_uri="memory://",  # Use in-memory storage for development
        enabled=app.config.get('RATE_LIMITING_ENABLED', True)
    )
    
    # Authentication rate limits
    limiter.limit("5 per minute")(app.view_functions.get('auth.login'))
    limiter.limit("3 per minute")(app.view_functions.get('auth.register'))
    limiter.limit("10 per hour")(app.view_functions.get('auth.google_login'))
    
    # Password change rate limits
    limiter.limit("3 per hour")(app.view_functions.get('auth.change_password'))
    
    # API rate limits
    limiter.limit("100 per hour")(app.view_functions.get('api.get_lessons'))
    limiter.limit("100 per hour")(app.view_functions.get('api.get_notes'))
    limiter.limit("50 per hour")(app.view_functions.get('api.create_lesson'))
    limiter.limit("50 per hour")(app.view_functions.get('api.create_note'))
    
    # File upload rate limits
    limiter.limit("20 per hour")(app.view_functions.get('api.upload_file'))
    
    # Pomodoro rate limits
    limiter.limit("200 per hour")(app.view_functions.get('api.pomodoro_start'))
    limiter.limit("200 per hour")(app.view_functions.get('api.pomodoro_stop'))
    
    return limiter

def get_rate_limit_config():
    """Get rate limiting configuration based on environment"""
    return {
        'development': {
            'enabled': False,  # Disable in development
            'storage': 'memory://',
            'default_limits': ["10000 per hour", "1000 per minute"]
        },
        'production': {
            'enabled': True,
            'storage': 'memory://',  # Could use Redis in production
            'default_limits': ["1000 per hour", "100 per minute"],
            'auth_limits': {
                'login': "5 per minute",
                'register': "3 per minute",
                'password_reset': "3 per hour",
                'google_oauth': "10 per hour"
            },
            'api_limits': {
                'general': "100 per hour",
                'create': "50 per hour",
                'upload': "20 per hour"
            }
        },
        'testing': {
            'enabled': False,
            'storage': 'memory://',
            'default_limits': ["10000 per hour"]
        }
    }

def create_rate_limiter(app):
    """Create and configure rate limiter for the app"""
    
    config = get_rate_limit_config()
    env = app.config.get('FLASK_ENV', 'development')
    rate_config = config.get(env, config['development'])
    
    if not rate_config['enabled']:
        return None
    
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=rate_config['default_limits'],
        storage_uri=rate_config['storage'],
        enabled=rate_config['enabled']
    )
    
    # Add custom rate limit decorators
    add_custom_limits(limiter, rate_config)
    
    return limiter

def add_custom_limits(limiter, config):
    """Add custom rate limits for specific endpoints"""
    
    # Authentication limits
    auth_limits = config.get('auth_limits', {})
    if auth_limits:
        @limiter.limit(auth_limits.get('login', "5 per minute"))
        def login_rate_limit():
            pass
            
        @limiter.limit(auth_limits.get('register', "3 per minute"))
        def register_rate_limit():
            pass
            
        @limiter.limit(auth_limits.get('password_reset', "3 per hour"))
        def password_reset_rate_limit():
            pass
            
        @limiter.limit(auth_limits.get('google_oauth', "10 per hour"))
        def google_oauth_rate_limit():
            pass
    
    # API limits
    api_limits = config.get('api_limits', {})
    if api_limits:
        @limiter.limit(api_limits.get('general', "100 per hour"))
        def api_general_rate_limit():
            pass
            
        @limiter.limit(api_limits.get('create', "50 per hour"))
        def api_create_rate_limit():
            pass
            
        @limiter.limit(api_limits.get('upload', "20 per hour"))
        def api_upload_rate_limit():
            pass

def get_client_ip():
    """Get client IP address for rate limiting"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return get_remote_address()
