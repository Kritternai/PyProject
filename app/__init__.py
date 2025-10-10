"""
Application factory following Clean Architecture principles.
Creates and configures Flask application with proper dependency injection.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config.settings import get_config
from .middleware.auth_middleware import load_user

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    
    # No dependency injection needed for simple MVC
    
    # Register middleware
    app.before_request(load_user)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register template context processors
    register_template_context_processors(app)
    
    # Register static file routes
    register_static_routes(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    import_models()
    
    return app


def register_blueprints(app):
    """
    Register application blueprints.
    
    Args:
        app: Flask application instance
    """
    # ============================================
    # MAIN ROUTES (Modular - Recommended)
    # ============================================
    from .routes.main_routes import main_routes_bp
    from .routes.class_routes import class_bp
    from .routes.classwork_routes import classwork_bp
    from .routes.note_web_routes import note_web_bp
    from .routes.api_routes import api_bp
    
    # ============================================
    # API ROUTES
    # ============================================
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.lesson_routes import lesson_bp
    from .routes.note_routes import note_bp
    from .routes.task_routes import task_bp
    from .routes.pomodoro_routes import pomodoro_bp
    
    # ============================================
    # INTEGRATION ROUTES
    # ============================================
    from .routes_google_classroom import google_classroom_bp
    from .routes_google_auth import google_auth_bp
    from .routes_microsoft_teams import microsoft_teams_bp

    # Register main routes (for HTML pages)
    app.register_blueprint(main_bp)
    app.register_blueprint(google_classroom_bp)  # Google Classroom integration
    app.register_blueprint(google_auth_bp)  # Google Sign-In (OAuth)
    app.register_blueprint(microsoft_teams_bp)  # Microsoft Teams integration (mockup)

    # ============================================
    # POMODORO SESSION ROUTES (from routes_new.py)
    # ============================================
    from .routes_new import main_bp as pomodoro_legacy_bp

    # ============================================
    # REGISTER MAIN WEB ROUTES
    # ============================================
    app.register_blueprint(main_routes_bp)  # /, /dashboard, /partial/dashboard, /partial/track, /partial/dev
    app.register_blueprint(class_bp)        # /partial/class, /class/<id>, class CRUD
    app.register_blueprint(note_web_bp)     # /partial/note, note fragments & CRUD
    app.register_blueprint(classwork_bp)    # /classwork/* tasks & materials
    app.register_blueprint(api_bp)          # /api/* general data endpoints
    
    # ============================================
    # REGISTER API BLUEPRINTS
    # ============================================
    app.register_blueprint(auth_bp)         # /api/auth/* 
    app.register_blueprint(user_bp)         # /api/users/*
    app.register_blueprint(lesson_bp)       # /api/lessons/*
    app.register_blueprint(note_bp)         # /api/notes/*
    app.register_blueprint(task_bp)         # /api/tasks/*
    app.register_blueprint(pomodoro_bp)     # /api/pomodoro/*
    
    # ============================================
    # REGISTER INTEGRATION BLUEPRINTS
    # ============================================
    app.register_blueprint(google_classroom_bp)   # Google Classroom
    app.register_blueprint(microsoft_teams_bp)    # Microsoft Teams
    
    # ============================================
    # REGISTER POMODORO SESSION ROUTES
    # ============================================
    app.register_blueprint(pomodoro_legacy_bp)  # /pomodoro/session/*, /pomodoro/statistics/*


def register_template_filters(app):
    """
    Register custom template filters.
    
    Args:
        app: Flask application instance
    """
    @app.template_filter('lesson_color_primary')
    def lesson_color_primary(color_id):
        """Get primary color for lesson - supports both selected_color and color_theme"""
        if color_id is None:
            return '#007bff'
        
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
        """Get secondary color for lesson - supports both selected_color and color_theme"""
        if color_id is None:
            return '#0056b3'
        
        colors = {
            1: '#0056b3',
            2: '#1e7e34',
            3: '#c82333', 
            4: '#e0a800',
            5: '#5a2d91',
            6: '#e8690b'
        }
        return colors.get(int(color_id), '#0056b3')

    @app.template_filter('get_lesson_color')
    def get_lesson_color(lesson):
        """Get color from lesson object - supports both selected_color and color_theme"""
        if hasattr(lesson, 'color_theme') and lesson.color_theme:
            return lesson.color_theme
        elif hasattr(lesson, 'selected_color') and lesson.selected_color:
            return lesson.selected_color
        else:
            return 1  # Default color

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


def register_template_context_processors(app):
    """
    Register template context processors.
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_user():
        """
        Inject user object into all templates.
        This makes the user object available in all templates.
        """
        from flask import g
        return dict(user=getattr(g, 'user', None))


def register_static_routes(app):
    """
    Register routes for serving static files from uploads folder.
    
    Args:
        app: Flask application instance
    """
    import os
    from flask import send_from_directory
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files from the uploads directory."""
        upload_folder = app.config.get('UPLOAD_FOLDER')
        return send_from_directory(upload_folder, filename)


def import_models():
    """
    Import all models to ensure they are registered with SQLAlchemy.
    This is necessary for database operations.
    """
    # Import MVC models
    from .models.user import UserModel
    from .models.lesson import LessonModel
    from .models.lesson_section import LessonSectionModel
    from .models.note import NoteModel
    from .models.task import TaskModel