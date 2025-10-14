#!/bin/bash

# =============================================================================
# Smart Learning Hub - Database & Flask Startup Script
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# =============================================================================
# 1. ENVIRONMENT SETUP
# =============================================================================
print_header "Smart Learning Hub - Environment Setup"

# Set Environment Variables
print_step "Setting environment variables..."

# Check if environment variables are already set
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    print_warning "Google OAuth credentials not found in environment variables"
    print_status "Please set the following environment variables:"
    print_status "export GOOGLE_CLIENT_ID='your-client-id-here'"
    print_status "export GOOGLE_CLIENT_SECRET='your-client-secret-here'"
    print_status "export FLASK_SECRET_KEY='your-strong-random-flask-secret-key'"
    print_warning "Using default development values..."
    
    # Set default development values (replace with your actual credentials)
    export GOOGLE_CLIENT_ID="your-google-client-id-here"
    export GOOGLE_CLIENT_SECRET="your-google-client-secret-here"
    export FLASK_SECRET_KEY="your_strong_random_flask_secret_key" # REMEMBER TO CHANGE THIS!    
else
    print_success "Google OAuth credentials found in environment variables"
fi

export OAUTHLIB_INSECURE_TRANSPORT="1"
export FLASK_ENV="development"
export FLASK_DEBUG="1"

print_status "Environment variables set successfully"

# =============================================================================
# 2. VIRTUAL ENVIRONMENT CHECK & ACTIVATION
# =============================================================================
print_step "Checking virtual environment..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Virtual environment found at venv/"
    source venv/bin/activate
    print_status "Virtual environment activated"
else
    print_warning "Virtual environment not found at venv/"
    print_step "Creating new virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    print_status "Virtual environment created and activated"
fi

# =============================================================================
# 3. DEPENDENCIES CHECK & INSTALLATION
# =============================================================================
print_step "Checking Python dependencies..."

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Requirements file found"
    
    # Check if key packages are installed
    if ! python -c "import flask" 2>/dev/null; then
        print_warning "Flask not found, installing dependencies..."
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_status "Key dependencies already installed"
    fi
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    
    # Install essential packages
    pip install flask sqlalchemy werkzeug
    print_status "Basic dependencies installed"
fi

# =============================================================================
# 4. DATABASE INITIALIZATION
# =============================================================================
print_step "Initializing database..."

# Check if database directory exists
if [ ! -d "database" ]; then
    print_error "Database directory not found!"
    print_error "Please ensure the database package is properly set up"
    exit 1
fi

# Check if database initialization script exists
if [ -f "init_database.py" ]; then
    print_status "Database initialization script found"
    
    # Check if database file exists
    if [ -f "instance/site.db" ]; then
        print_status "Database file exists, checking health..."
        
        # Test database health
        if python test_database.py >/dev/null 2>&1; then
            print_status "Database is healthy and ready"
        else
            print_warning "Database health check failed, reinitializing..."
            python init_database.py
        fi
    else
        print_status "Database file not found, creating new database..."
        python init_database.py
        
        if [ $? -eq 0 ]; then
            print_status "Database created successfully"
        else
            print_error "Failed to create database"
            exit 1
        fi
    fi
else
    print_error "Database initialization script not found!"
    print_error "Please ensure init_database.py exists"
    exit 1
fi

# =============================================================================
# 5. DATABASE BACKUP (OPTIONAL)
# =============================================================================
print_step "Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p database/backups

# Create backup with timestamp
BACKUP_FILE="database/backups/pre_startup_backup_$(date +%Y%m%d_%H%M%S).db"
if cp instance/site.db "$BACKUP_FILE" 2>/dev/null; then
    print_status "Database backup created: $BACKUP_FILE"
else
    print_warning "Failed to create database backup"
fi

# =============================================================================
# 6. FLASK APPLICATION STARTUP
# =============================================================================
print_header "Starting Flask Application"

# Set Flask application
export FLASK_APP=run.py

# Check if run.py exists
if [ ! -f "run.py" ]; then
    print_error "run.py not found!"
    print_error "Please ensure the Flask application file exists"
    exit 1
fi

print_status "Flask application file: run.py"
print_status "Environment: $FLASK_ENV"
print_status "Debug mode: $FLASK_DEBUG"

# =============================================================================
# 7. FINAL CHECKS & STARTUP
# =============================================================================
print_step "Performing final checks..."

# Check if all required files exist
REQUIRED_FILES=("run.py" "app/__init__.py" "database/__init__.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done

print_status "All required files found"

# Check database one more time
print_step "Final database health check..."
if python -c "
from database import get_db_manager
manager = get_db_manager()
if manager.health_check():
    print('Database is healthy')
    exit(0)
else:
    print('Database health check failed')
    exit(1)
" 2>/dev/null; then
    print_status "Database health check passed"
else
    print_error "Final database health check failed"
    exit 1
fi

# =============================================================================
# 8. START FLASK APPLICATION
# =============================================================================
print_header "🚀 Starting Smart Learning Hub Flask Application 🚀"

print_status "Application will be available at: http://localhost:8000 (or 8001 if busy)"
print_status "Press Ctrl+C to stop the application"
echo ""

# Start Flask application
print_step "Starting Flask development server..."

# Start Flask on port 8000 (avoid macOS AirPlay port 5000)
PORT=8000
print_status "Starting Flask on port $PORT (avoiding macOS AirPlay port 5000)..."

# Check if port is available
if timeout 5 bash -c "echo >/dev/tcp/localhost/$PORT" 2>/dev/null; then
    print_warning "Port $PORT is busy, trying port 8001..."
    PORT=8001
fi

print_status "Flask will be available at: http://localhost:$PORT"
flask run --host=0.0.0.0 --port=$PORT

# =============================================================================
# 9. CLEANUP ON EXIT
# =============================================================================
cleanup() {
    echo ""
    print_header "Shutting Down Smart Learning Hub"
    print_status "Cleaning up..."
    
    # Deactivate virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        print_status "Virtual environment deactivated"
    fi
    
    print_status "Goodbye! 👋"
    exit 0
}

# Set trap to call cleanup function on script exit
trap cleanup EXIT INT TERM
