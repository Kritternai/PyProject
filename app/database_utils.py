"""
Database utilities to avoid circular imports
"""

def get_db():
    """Get database instance safely avoiding circular imports"""
    try:
        # Try to get from current app context first
        from flask import current_app
        if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
            return current_app.extensions['sqlalchemy']
    except (ImportError, RuntimeError):
        pass
    
    try:
        # Fallback to direct import (only when app is fully loaded)
        from flask_sqlalchemy import SQLAlchemy
        from flask import Flask
        
        # Get current app if available
        try:
            from flask import current_app
            return current_app.extensions['sqlalchemy']
        except (RuntimeError, KeyError):
            # Create new instance if no app context
            return SQLAlchemy()
    except ImportError:
        # Last resort fallback
        from flask_sqlalchemy import SQLAlchemy
        return SQLAlchemy()

def get_db_session():
    """Get database session safely"""
    db = get_db()
    return db.session