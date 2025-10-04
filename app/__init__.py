"""
Application factory following Clean Architecture principles.
Creates and configures Flask application with proper dependency injection.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config.settings import get_config
from .infrastructure.di.container import configure_services
from .presentation.middleware.auth_middleware import load_user

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
    
    # Configure dependency injection
    configure_services()
    
    # Register middleware
    app.before_request(load_user)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    import_models()
    
    return app


def register_blueprints(app):
    """
    Register application blueprints.
    
    Args:
        app: Flask application instance
    """
    from .presentation.routes.auth_routes import auth_bp
    from .presentation.routes.user_routes import user_bp
    from .presentation.routes.lesson_routes import lesson_bp
    from .presentation.routes.note_routes import note_bp
    from .presentation.routes.task_routes import task_bp
    from .presentation.routes.web_routes import web_bp
    from .presentation.routes.register_routes import register_bp
    # from .presentation.routes.pomodoro_routes import pomodoro_bp  # Removed old Pomodoro system
    from .presentation.routes.tracking_routes import tracking_bp
    from .presentation.routes.announcement_routes import announcement_bp
    from .presentation.routes.class_note_routes import class_note_bp
    from .routes_new import main_bp as main_bp
    from .routes_google_classroom import google_classroom_bp
    from .routes_microsoft_teams import microsoft_teams_bp
    # from .routes import main_bp as legacy_bp  # Temporarily disabled due to route conflicts
    
    # Register main routes (for HTML pages)
    app.register_blueprint(main_bp)
    app.register_blueprint(google_classroom_bp)  # Google Classroom integration
    app.register_blueprint(microsoft_teams_bp)  # Microsoft Teams integration (mockup)
    # app.register_blueprint(legacy_bp)  # Legacy routes temporarily disabled - most routes now in routes_new.py
    app.register_blueprint(register_bp)
    # app.register_blueprint(pomodoro_bp)  # Removed old Pomodoro system
    app.register_blueprint(tracking_bp)
    
    # Register API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(note_bp)
    app.register_blueprint(task_bp)
    
    # Register Class System blueprints
    app.register_blueprint(announcement_bp)
    app.register_blueprint(class_note_bp)
    
    # Register Pomodoro OOP blueprints
    from .presentation.routes.pomodoro_routes_new import pomodoro_bp as pomodoro_new_bp
    app.register_blueprint(pomodoro_new_bp)


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


def import_models():
    """
    Import all models to ensure they are registered with SQLAlchemy.
    This is necessary for database operations.
    """
    # Import legacy models for backward compatibility (selective)
    # Register Files model to support note attachments
    from .core.files import Files
    # from .core.imported_data import ImportedData
    # from .core.google_credentials import GoogleCredentials
    # from .core.course_linkage import CourseLinkage
    
    # Import new infrastructure models
    from .infrastructure.database.models.user_model import UserModel
    from .infrastructure.database.models.lesson_model import LessonModel
    from .infrastructure.database.models.lesson_section_model import LessonSectionModel
    from .infrastructure.database.models.note_model import NoteModel
    from .infrastructure.database.models.task_model import TaskModel