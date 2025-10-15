#!/bin/bash
# Build script for Render deployment

echo "🚀 Building Smart Learning Hub for Render..."

# Install dependencies
pip install -r requirements-production.txt

# Create necessary directories
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
