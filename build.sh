#!/bin/bash
# Build script for SQLite deployment on Render

echo "🚀 Building Smart Learning Hub with SQLite..."

# Upgrade pip first
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies with verbose output
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt --verbose

# Check Python environment
echo "🐍 Python environment info..."
python --version
which python
pip --version
echo "PYTHONPATH: $PYTHONPATH"

# Verify pip installation
echo "🔍 Checking pip installation..."
pip list | grep -i flask

# Verify critical dependencies with detailed error info
echo "🔍 Verifying critical dependencies..."
python -c "
import sys
print(f'Python executable: {sys.executable}')
print(f'Python path: {sys.path}')

try:
    import flask
    print('✅ Flask installed successfully')
    print(f'Flask version: {flask.__version__}')
    print(f'Flask location: {flask.__file__}')
except ImportError as e:
    print(f'❌ Flask not found: {e}')
    print('Available modules:')
    import pkgutil
    for importer, modname, ispkg in pkgutil.iter_modules():
        if 'flask' in modname.lower():
            print(f'  - {modname}')
    exit(1)

try:
    import sqlalchemy
    print('✅ SQLAlchemy installed successfully')
    print(f'SQLAlchemy version: {sqlalchemy.__version__}')
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
