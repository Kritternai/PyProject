"""
Database instance module to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy

# Create db instance that can be imported safely
db = SQLAlchemy()