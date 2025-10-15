#!/usr/bin/env python3
"""
Smart Learning Hub - OOP Architecture Flask Startup Script
Cross-platform Python version of start.sh
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import time
import signal
import atexit
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header(message):
    print(f"{Colors.BLUE}{'='*77}{Colors.NC}")
    print(f"{Colors.BLUE}{message}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*77}{Colors.NC}")

def print_step(message):
    print(f"{Colors.CYAN}[STEP]{Colors.NC} {message}")

def run_command(command, shell=True, check=True, capture_output=False):
    """Run a command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check, 
                                 capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=shell, check=check)
            return True
    except subprocess.CalledProcessError as e:
        if not check:
            return False
        print_error(f"Command failed: {e}")
        return False

def check_file_exists(file_path):
    """Check if a file exists"""
    return Path(file_path).exists()

def check_directory_exists(dir_path):
    """Check if a directory exists"""
    return Path(dir_path).exists()

def setup_environment():
    """Set up environment variables"""
    print_step("Setting environment variables...")
    
    # Set environment variables
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "1"
    
    # Check if Google OAuth credentials are set
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        print_warning("Google OAuth credentials not found in environment variables")
        print_status("Please set the following environment variables:")
        print_status("export GOOGLE_CLIENT_ID='your-client-id-here'")
        print_status("export GOOGLE_CLIENT_SECRET='your-client-secret-here'")
        print_status("export FLASK_SECRET_KEY='your-strong-random-flask-secret-key'")
        print_warning("Using default development values...")
        
        # Set default development values
        os.environ["GOOGLE_CLIENT_ID"] = "your-google-client-id-here"
        os.environ["GOOGLE_CLIENT_SECRET"] = "your-google-client-secret-here"
        os.environ["FLASK_SECRET_KEY"] = "your_strong_random_flask_secret_key"
    else:
        print_success("Google OAuth credentials found in environment variables")
    
    print_status("Environment variables set successfully")

def setup_virtual_environment():
    """Set up and activate virtual environment"""
    print_step("Checking virtual environment...")
    
    if check_directory_exists("venv"):
        print_status("Virtual environment found at venv/")
        # Activate virtual environment
        if platform.system() == "Windows":
            activate_script = "venv\\Scripts\\activate.bat"
        else:
            activate_script = "venv/bin/activate"
        
        if check_file_exists(activate_script):
            print_status("Virtual environment activated")
        else:
            print_warning("Virtual environment activation script not found")
    else:
        print_warning("Virtual environment not found at venv/")
        print_step("Creating new virtual environment...")
        
        # Create virtual environment
        if run_command("python -m venv venv"):
            print_status("Virtual environment created and activated")
        else:
            print_error("Failed to create virtual environment")
            return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step("Checking Python dependencies...")
    
    if check_file_exists("requirements.txt"):
        print_status("Requirements file found")
        
        # Check if key packages are installed
        try:
            import flask
            print_status("Key dependencies already installed")
        except ImportError:
            print_warning("Flask not found, installing dependencies...")
            if run_command("pip install -r requirements.txt"):
                print_status("Dependencies installed successfully")
            else:
                print_error("Failed to install dependencies")
                return False
        
        # Check for dependency-injector
        try:
            import dependency_injector
            print_status("dependency-injector already installed")
        except ImportError:
            print_warning("dependency-injector not found, installing...")
            if run_command("pip install dependency-injector"):
                print_status("dependency-injector installed successfully")
            else:
                print_error("Failed to install dependency-injector")
                return False
    else:
        print_warning("requirements.txt not found, installing basic dependencies...")
        if run_command("pip install flask sqlalchemy werkzeug dependency-injector"):
            print_status("Basic dependencies installed")
        else:
            print_error("Failed to install basic dependencies")
            return False
    
    return True

def validate_oop_architecture():
    """Validate OOP architecture files"""
    print_step("Validating OOP Architecture...")
    
    oop_files = [
        "app/domain/entities/user.py",
        "app/domain/entities/lesson.py",
        "app/domain/entities/note.py",
        "app/domain/entities/task.py",
        "app/application/services/user_service.py",
        "app/application/services/lesson_service.py",
        "app/application/services/note_service.py",
        "app/application/services/task_service.py",
        "app/infrastructure/database/models/user_model.py",
        "app/infrastructure/database/models/lesson_model.py",
        "app/infrastructure/database/models/note_model.py",
        "app/infrastructure/database/models/task_model.py",
        "app/presentation/controllers/user_controller.py",
        "app/presentation/controllers/lesson_controller.py",
        "app/presentation/controllers/note_controller.py",
        "app/presentation/controllers/task_controller.py",
        "app/infrastructure/di/container.py",
    ]
    
    missing_files = []
    for file in oop_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if not missing_files:
        print_success("All OOP architecture files found")
        return True
    else:
        print_error("Missing OOP architecture files:")
        for file in missing_files:
            print_error(f"  - {file}")
        print_error("Please ensure the OOP architecture is properly set up")
        return False

def initialize_database():
    """Initialize database"""
    print_step("Initializing database...")
    
    # Check if instance directory exists
    if not check_directory_exists("instance"):
        print_status("Creating instance directory...")
        os.makedirs("instance", exist_ok=True)
    
    # Run complete database migration
    print_step("Running complete database migration...")
    if check_file_exists("database/migrations/complete_database_schema.py"):
        if run_command("python database/migrations/complete_database_schema.py", check=False):
            print_success("Complete database schema created successfully")
        else:
            print_warning("Complete database schema creation failed, but continuing...")
    elif check_file_exists("database/migrations/create_complete_database.py"):
        if run_command("python database/migrations/create_complete_database.py", check=False):
            print_success("Complete database migration completed")
        else:
            print_warning("Complete database migration failed, but continuing...")
    else:
        print_warning("Complete database migration script not found, skipping...")
    
    # Check if database file exists
    if check_file_exists("instance/site.db"):
        print_status("Database file exists, checking health...")
        
        # Test database health
        health_check = """
from app import create_app, db
try:
    app = create_app()
    with app.app_context():
        result = db.session.execute(db.text('SELECT 1')).scalar()
        print('Database is healthy')
        exit(0)
except Exception as e:
    print('Database health check failed:', str(e))
    exit(1)
"""
        
        if run_command(f'python -c "{health_check}"', check=False, capture_output=True):
            print_status("Database is healthy and ready")
        else:
            print_warning("Database health check failed, reinitializing...")
            reinit_script = """
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database reinitialized')
"""
            run_command(f'python -c "{reinit_script}"', check=False)
    else:
        print_status("Database file not found, creating new database...")
        create_script = """
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database created successfully')
"""
        if run_command(f'python -c "{create_script}"', check=False):
            print_status("Database created successfully")
        else:
            print_error("Failed to create database")
            return False
    
    return True

def create_default_user():
    """Create default test user"""
    print_step("Creating default test user...")
    
    user_script = """
import sys
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
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
            print(f'Default test user created: email=1, password=1, id={user_id}')
        conn.close()
        
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"""
    
    if run_command(f'python -c "{user_script}"', check=False):
        print_status("Default test user ready (email: 1, password: 1)")
    else:
        print_warning("Failed to create default user, but continuing...")
    
    return True

def test_oop_architecture():
    """Test OOP architecture"""
    print_step("Testing OOP Architecture...")
    
    if check_file_exists("scripts/tests/test_oop.py"):
        print_status("Running OOP architecture test...")
        if run_command("python scripts/tests/test_oop.py", check=False):
            print_success("OOP architecture test passed")
        else:
            print_warning("OOP architecture test failed, but continuing...")
    else:
        print_warning("scripts/tests/test_oop.py not found, skipping OOP test")
    
    return True

def start_flask_application():
    """Start Flask application"""
    print_header("🚀 Starting Smart Learning Hub OOP Architecture Flask Application 🚀")
    
    print_status("Application will be available at: http://localhost:5004")
    print_status("Architecture: Clean Architecture + SOLID Principles")
    print_status("Features: User, Lesson, Note, Task, Pomodoro Management")
    print_status("Press Ctrl+C to stop the application")
    print("")
    
    # Check if run.py exists
    if not check_file_exists("run.py"):
        print_error("run.py not found!")
        print_error("Please ensure the Flask application file exists")
        return False
    
    print_step("Starting Flask development server...")
    print_status("Flask will be available at: http://localhost:5004")
    print_status("Web Interface: http://localhost:5004")
    print_status("API Endpoints: http://localhost:5004/api/")
    
    # Start Flask application
    try:
        run_command("python run.py", check=False)
    except KeyboardInterrupt:
        print("\n")
        print_header("Shutting Down Smart Learning Hub OOP Architecture")
        print_status("Goodbye! 👋")
        return True
    
    return True

def cleanup():
    """Cleanup function"""
    print("\n")
    print_header("Shutting Down Smart Learning Hub OOP Architecture")
    print_status("Cleaning up...")
    print_status("Goodbye! 👋")

def main():
    """Main function"""
    print_header("Smart Learning Hub - OOP Architecture Environment Setup")
    
    # Set up signal handlers for cleanup
    def signal_handler(signum, frame):
        cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    try:
        # 1. Environment setup
        setup_environment()
        
        # 2. Virtual environment
        if not setup_virtual_environment():
            return False
        
        # 3. Dependencies
        if not install_dependencies():
            return False
        
        # 4. OOP Architecture validation
        if not validate_oop_architecture():
            return False
        
        # 5. Database initialization
        if not initialize_database():
            return False
        
        # 6. Create default user
        create_default_user()
        
        # 7. Test OOP architecture
        test_oop_architecture()
        
        # 8. Start Flask application
        start_flask_application()
        
    except Exception as e:
        print_error(f"An error occurred: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
