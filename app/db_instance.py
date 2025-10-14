"""Shared SQLAlchemy instance for avoiding circular imports."""
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance used across models and services
# Import this object instead of creating new SQLAlchemy() to prevent circular imports.
db = SQLAlchemy()


def init_db(app):
    """Initialize SQLAlchemy with the given Flask app."""
    db.init_app(app)
