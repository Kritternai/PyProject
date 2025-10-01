#!/bin/bash

# =============================================================================
# Smart Learning Hub - Simple Startup Script
# =============================================================================

echo "🚀 Starting Smart Learning Hub..."

# Set Environment Variables
export GOOGLE_CLIENT_ID="40820229782-0f7uoqd5ab94cuipmbdk09jeradqvac0.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="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"
export FLASK_SECRET_KEY="your_strong_random_flask_secret_key"
export OAUTHLIB_INSECURE_TRANSPORT="1"
export FLASK_ENV="development"
export FLASK_DEBUG="1"

# Activate Virtual Environment
if [ -d "/Users/kbbk/PyProject-1/venv" ]; then
    source /Users/kbbk/PyProject-1/venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found, creating new one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask sqlalchemy werkzeug
    echo "✅ Virtual environment created and dependencies installed"
fi

# Initialize Database
if [ -f "init_database.py" ]; then
    if [ ! -f "instance/site.db" ]; then
        echo "🗄️  Creating database..."
        python init_database.py
    else
        echo "✅ Database already exists"
    fi
else
    echo "❌ Database initialization script not found!"
    exit 1
fi

# Set Flask App
export FLASK_APP=run.py

# Start Flask
echo "🌐 Starting Flask application at http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Start Flask on port 8000 (avoid macOS AirPlay port 5000)
PORT=8000
echo "🌐 Starting Flask on port $PORT (avoiding macOS AirPlay port 5000)..."

# Check if port is available
if timeout 5 bash -c "echo >/dev/tcp/localhost/$PORT" 2>/dev/null; then
    echo "⚠️  Port $PORT is busy, trying port 8001..."
    PORT=8001
fi

echo "✅ Flask will be available at: http://localhost:$PORT"
flask run --host=0.0.0.0 --port=$PORT
