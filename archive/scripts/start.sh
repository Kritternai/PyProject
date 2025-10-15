#!/bin/bash

# =============================================================================
# Smart Learning Hub - OOP Architecture Flask Startup Script
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
print_header "Smart Learning Hub - OOP Architecture Environment Setup"

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
    
    # Check for dependency-injector
    if ! python -c "import dependency_injector" 2>/dev/null; then
        print_warning "dependency-injector not found, installing..."
        pip install dependency-injector
        print_status "dependency-injector installed successfully"
    else
        print_status "dependency-injector already installed"
    fi
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    
    # Install essential packages
    pip install flask sqlalchemy werkzeug dependency-injector
    print_status "Basic dependencies installed"
fi

# =============================================================================
# 4. OOP ARCHITECTURE VALIDATION
# =============================================================================
print_step "Validating OOP Architecture..."

# Check if OOP architecture files exist
OOP_FILES=(
    "app/domain/entities/user.py"
    "app/domain/entities/lesson.py"
    "app/domain/entities/note.py"
    "app/domain/entities/task.py"
    "app/application/services/user_service.py"
    "app/application/services/lesson_service.py"
    "app/application/services/note_service.py"
    "app/application/services/task_service.py"
    "app/infrastructure/database/models/user_model.py"
    "app/infrastructure/database/models/lesson_model.py"
    "app/infrastructure/database/models/note_model.py"
    "app/infrastructure/database/models/task_model.py"
    "app/presentation/controllers/user_controller.py"
    "app/presentation/controllers/lesson_controller.py"
    "app/presentation/controllers/note_controller.py"
    "app/presentation/controllers/task_controller.py"
    "app/infrastructure/di/container.py"
)

missing_files=()
for file in "${OOP_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    print_success "All OOP architecture files found"
else
    print_error "Missing OOP architecture files:"
    for file in "${missing_files[@]}"; do
        print_error "  - $file"
    done
    print_error "Please ensure the OOP architecture is properly set up"
    exit 1
fi

# =============================================================================
# 5. DATABASE INITIALIZATION
# =============================================================================
print_step "Initializing database..."

# Check if database directory exists
if [ ! -d "instance" ]; then
    print_status "Creating instance directory..."
    mkdir -p instance
fi

# Run complete database migration
print_step "Running complete database migration..."
if [ -f "database/migrations/create_complete_database.py" ]; then
    if PYTHONPATH=. python database/migrations/create_complete_database.py; then
        print_success "Complete database migration completed"
    else
        print_warning "Complete database migration failed, but continuing..."
    fi
else
    print_warning "Complete database migration script not found, skipping..."
fi

# Check if database file exists
if [ -f "instance/site.db" ]; then
    print_status "Database file exists, checking health..."
    
    # Test database health with new architecture
    if PYTHONPATH=. python -c "
from app import create_app, db
from app.infrastructure.di.container import configure_services
try:
    app = create_app()
    configure_services()
    with app.app_context():
        result = db.session.execute(db.text('SELECT 1')).scalar()
        print('Database is healthy')
        exit(0)
except Exception as e:
    print('Database health check failed:', str(e))
    exit(1)
" 2>/dev/null; then
        print_status "Database is healthy and ready"
    else
        print_warning "Database health check failed, reinitializing..."
        PYTHONPATH=. python -c "
from app import create_app, db
from app.infrastructure.di.container import configure_services
app = create_app()
configure_services()
with app.app_context():
    db.create_all()
    print('Database reinitialized')
"
    fi
else
    print_status "Database file not found, creating new database..."
    PYTHONPATH=. python -c "
from app import create_app, db
from app.infrastructure.di.container import configure_services
app = create_app()
configure_services()
with app.app_context():
    db.create_all()
    print('Database created successfully')
"
    
    if [ $? -eq 0 ]; then
        print_status "Database created successfully"
    else
        print_error "Failed to create database"
        exit 1
    fi
fi

# =============================================================================
# 5.5. CREATE DEFAULT USER (OOP Architecture)
# =============================================================================
print_step "Creating default test user..."

PYTHONPATH=. python -c "
import sys
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

try:
    # Use OOP Architecture
    from app import create_app, db
    from app.infrastructure.di.container import get_service
    from app.domain.interfaces.services.user_service import UserService
    from app.domain.value_objects.email import Email
    from app.domain.value_objects.password import Password
    
    app = create_app()
    with app.app_context():
        try:
            user_service = get_service(UserService)
            
            # Check if user exists
            from app.domain.interfaces.repositories.user_repository import UserRepository
            user_repo = get_service(UserRepository)
            existing = user_repo.get_by_email(Email('1'))
            
            if existing:
                print('Default test user already exists')
            else:
                # Create user with OOP architecture
                # Use longer username to pass validation (min 3 chars)
                email = Email('1')
                password = Password('1')
                user = user_service.create_user(email=email, password=password, username='user1')
                print(f'Default test user created: email=1, password=1, username=user1, id={user.id}')
        except Exception as e:
            # Fallback: use direct SQL if OOP fails
            print(f'OOP creation failed, using SQL fallback...')
            import sqlite3
            password_hash = generate_password_hash('1')
            user_id = str(uuid.uuid4())
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            conn = sqlite3.connect('instance/site.db')
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT id FROM user WHERE email = ?', ('1',))
            if cursor.fetchone():
                print('Default test user already exists')
            else:
                cursor.execute('''
                    INSERT INTO user (id, username, email, password_hash, role, is_active, 
                                    email_verified, created_at, updated_at, total_lessons, 
                                    total_notes, total_tasks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, '1', '1', password_hash, 'student', 1, 0, 
                      created_at, created_at, 0, 0, 0))
                conn.commit()
                print(f'Default test user created via SQL: email=1, password=1, id={user_id}')
            conn.close()
            
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 2>&1

if [ $? -eq 0 ]; then
    print_status "Default test user ready (email: 1, password: 1)"
else
    print_warning "Failed to create default user, but continuing..."
fi

# =============================================================================
# 6. OOP ARCHITECTURE TEST
# =============================================================================
print_step "Testing OOP Architecture..."

# Run OOP architecture test
if [ -f "scripts/tests/test_oop.py" ]; then
    print_status "Running OOP architecture test..."
    if PYTHONPATH=. python scripts/tests/test_oop.py >/dev/null 2>&1; then
        print_success "OOP architecture test passed"
    else
        print_warning "OOP architecture test failed, but continuing..."
    fi
else
    print_warning "scripts/tests/test_oop.py not found, skipping OOP test"
fi

# =============================================================================
# 7. FLASK APPLICATION STARTUP
# =============================================================================
print_header "Starting OOP Architecture Flask Application"

# Check if run_new.py exists
if [ ! -f "scripts/run_new.py" ]; then
    print_error "scripts/run_new.py not found!"
    print_error "Please ensure the OOP Flask application file exists"
    exit 1
fi

print_status "Flask application file: scripts/run_new.py"
print_status "Architecture: Clean Architecture + SOLID Principles"
print_status "Environment: $FLASK_ENV"
print_status "Debug mode: $FLASK_DEBUG"

# =============================================================================
# 8. FINAL CHECKS & STARTUP
# =============================================================================
print_step "Performing final checks..."

# Check if all required files exist
REQUIRED_FILES=("scripts/run_new.py" "app/__init__.py" "app/infrastructure/di/container.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done

print_status "All required files found"

# Check OOP architecture one more time
print_step "Final OOP architecture check..."
if PYTHONPATH=. python -c "
from app import create_app
from app.infrastructure.di.container import configure_services
try:
    app = create_app()
    configure_services()
    print('OOP architecture is healthy')
    exit(0)
except Exception as e:
    print('OOP architecture check failed:', str(e))
    exit(1)
" 2>/dev/null; then
    print_status "OOP architecture check passed"
else
    print_error "Final OOP architecture check failed"
    exit 1
fi

# =============================================================================
# 9. START FLASK APPLICATION
# =============================================================================
print_header "🚀 Starting Smart Learning Hub OOP Architecture Flask Application 🚀"

print_status "Application will be available at: http://localhost:5003"
print_status "Architecture: Clean Architecture + SOLID Principles"
print_status "Features: User, Lesson, Note, Task Management"
print_status "Press Ctrl+C to stop the application"
echo ""

# Start Flask application
print_step "Starting OOP Flask development server..."

# Start Flask on port 5003 (avoid macOS AirPlay port 5000)
PORT=5003
print_status "Starting OOP Flask on port $PORT..."

# Check if port is available
if timeout 5 bash -c "echo >/dev/tcp/localhost/$PORT" 2>/dev/null; then
    print_warning "Port $PORT is busy, trying port 5004..."
    PORT=5004
fi

print_status "OOP Flask will be available at: http://localhost:$PORT"
print_status "Web Interface: http://localhost:$PORT"
print_status "API Endpoints: http://localhost:$PORT/api/"

# Update run_new.py with the correct port if needed
if [ "$PORT" != "5003" ]; then
    print_status "Updating scripts/run_new.py to use port $PORT..."
    sed -i.bak "s/port=5003/port=$PORT/" scripts/run_new.py
fi

# Start the OOP Flask application
# Add current directory to PYTHONPATH so that 'app' module can be imported
PYTHONPATH=. python scripts/run_new.py

# =============================================================================
# 10. CLEANUP ON EXIT
# =============================================================================
cleanup() {
    echo ""
    print_header "Shutting Down Smart Learning Hub OOP Architecture"
    print_status "Cleaning up..."
    
    # Restore original run_new.py if it was modified
    if [ -f "scripts/run_new.py.bak" ]; then
        mv scripts/run_new.py.bak scripts/run_new.py
        print_status "Restored original scripts/run_new.py"
    fi
    
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

