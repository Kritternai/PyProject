#!/bin/bash
# Build script for Render deployment

echo "🚀 Building Smart Learning Hub for Render..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-production.txt

# Verify gunicorn installation
echo "🔍 Verifying gunicorn installation..."
python -c "import gunicorn; print('✅ Gunicorn installed successfully')" || {
    echo "❌ Gunicorn not found, installing..."
    pip install gunicorn==21.2.0
}

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
