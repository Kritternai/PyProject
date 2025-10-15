#!/bin/bash
# Build script for Render deployment

echo "🚀 Building Smart Learning Hub for Render..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install psycopg2-binary explicitly for PostgreSQL
echo "🐘 Installing PostgreSQL driver..."
pip install psycopg2-binary==2.9.9

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
python -c "
try:
    import psycopg2
    print('✅ psycopg2 imported successfully')
except ImportError as e:
    print(f'❌ psycopg2 import failed: {e}')
    exit(1)

try:
    import gunicorn
    print('✅ Gunicorn installed successfully')
except ImportError as e:
    print(f'❌ Gunicorn not found: {e}')
    exit(1)

try:
    import flask
    print('✅ Flask installed successfully')
except ImportError as e:
    print(f'❌ Flask not found: {e}')
    exit(1)
"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p instance uploads logs

# Run database migrations (if needed)
echo "📊 Setting up database..."
python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('✅ PostgreSQL database tables created successfully')
"

# Optional: Run migration script if needed
# echo "🔄 Running migration script..."
# python migrate_to_postgresql.py

echo "✅ Build completed successfully!"
