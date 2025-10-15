#!/bin/bash
# Build script for SQLite deployment on Render

echo "🚀 Building Smart Learning Hub with SQLite..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
python -c "
try:
    import flask
    print('✅ Flask installed successfully')
except ImportError as e:
    print(f'❌ Flask not found: {e}')
    exit(1)

try:
    import sqlalchemy
    print('✅ SQLAlchemy installed successfully')
except ImportError as e:
    print(f'❌ SQLAlchemy not found: {e}')
    exit(1)
"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p instance uploads logs

# Run database setup
echo "📊 Setting up SQLite database..."
python database/setup_database.py

echo "✅ Build completed successfully!"
