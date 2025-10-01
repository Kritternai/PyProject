"""
Application entry point with new Clean Architecture.
"""

from app import create_app, db

# Create application instance
app = create_app()

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)