#!/bin/bash
# Alternative build script specifically for Render deployment

echo "🚀 Building Smart Learning Hub for Render..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Check Python environment
echo "🐍 Python environment:"
python --version
which python
pip --version

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies with force reinstall
echo "📦 Installing dependencies..."
pip install --force-reinstall -r requirements.txt

# Verify installation
echo "🔍 Verifying installation..."
python -c "
import sys
print(f'Python path: {sys.path}')

# Test Flask
try:
    import flask
    print(f'✅ Flask {flask.__version__} installed')
except ImportError as e:
    print(f'❌ Flask import failed: {e}')
    exit(1)

# Test other critical modules
modules = ['sqlalchemy', 'werkzeug', 'jinja2']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module} installed')
    except ImportError as e:
        print(f'❌ {module} import failed: {e}')
        exit(1)

print('✅ All critical modules imported successfully')
"

# Create directories
echo "📁 Creating directories..."
mkdir -p instance uploads logs

# Setup database
echo "📊 Setting up database..."
python database/setup_database.py

echo "✅ Build completed successfully!"
