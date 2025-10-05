#!/usr/bin/env python3
"""
Smart Learning Hub - Complete Server Startup Script
Includes database setup, user creation, and Flask server startup
"""

import os
import sys
import subprocess
import venv
import socket
import sqlite3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
from typing import List


def print_status(msg: str) -> None:
    print(f"[INFO] {msg}")


def print_success(msg: str) -> None:
    print(f"[SUCCESS] {msg}")


def print_warning(msg: str) -> None:
    print(f"[WARNING] {msg}")


def print_error(msg: str) -> None:
    print(f"[ERROR] {msg}")


def print_header(msg: str) -> None:
    print("=" * 77)
    print(msg)
    print("=" * 77)


def in_venv() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def ensure_venv() -> None:
    if os.path.isdir("venv"):
        return
    print_status("Creating virtual environment at venv/ ...")
    venv.create("venv", with_pip=True)


def venv_python() -> str:
    if os.name == "nt":
        return os.path.join("venv", "Scripts", "python.exe")
    return os.path.join("venv", "bin", "python")


def reexec_in_venv() -> None:
    if in_venv():
        return
    ensure_venv()
    py = venv_python()
    print_status("Re-executing inside virtual environment...")
    os.execv(py, [py] + sys.argv)


def set_env_defaults() -> None:
    """Set environment variables with defaults"""
    print_status("Setting environment variables...")
    
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        print_warning("Google OAuth credentials not found in environment variables")
        print_status("Please set the following environment variables:")
        print_status("export GOOGLE_CLIENT_ID='your-client-id-here'")
        print_status("export GOOGLE_CLIENT_SECRET='your-client-secret-here'")
        print_status("export FLASK_SECRET_KEY='your-strong-random-flask-secret-key'")
        print_warning("Using default development values...")
        os.environ.setdefault("GOOGLE_CLIENT_ID", "231151462337-sspbadu0r8rlnoht5pgg77un10i26r8d.apps.googleusercontent.com")
        os.environ.setdefault("GOOGLE_CLIENT_SECRET", "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")
        os.environ.setdefault("FLASK_SECRET_KEY", "your_strong_random_flask_secret_key")
    
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("FLASK_DEBUG", "1")
    print_success("Environment variables set successfully")


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check)


def run_quiet(cmd: List[str]) -> bool:
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def ensure_dependencies() -> None:
    """Check and install Python dependencies"""
    print_status("Checking Python dependencies...")
    
    if os.path.isfile("requirements.txt"):
        if not run_quiet([sys.executable, "-c", "import flask"]):
            print_warning("Flask not found, installing dependencies...")
            run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        if not run_quiet([sys.executable, "-c", "import dependency_injector"]):
            print_warning("dependency-injector not found, installing...")
            run([sys.executable, "-m", "pip", "install", "dependency-injector"])
        print_success("Key dependencies already installed")
        print_success("dependency-injector already installed")
    else:
        print_warning("requirements.txt not found, installing basic dependencies...")
        run([sys.executable, "-m", "pip", "install", "flask", "sqlalchemy", "werkzeug", "dependency-injector"])


def validate_oop_files() -> None:
    """Validate OOP architecture files"""
    print_status("Validating OOP Architecture...")
    
    required = [
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
    
    missing = [p for p in required if not os.path.isfile(p)]
    if missing:
        print_error("Missing OOP architecture files:")
        for m in missing:
            print_error(f"  - {m}")
        sys.exit(1)
    
    print_success("All OOP architecture files found")


def setup_database() -> None:
    """Setup complete database schema"""
    print_status("Initializing database...")
    
    # Check if instance directory exists
    if not os.path.exists("instance"):
        print_status("Creating instance directory...")
        os.makedirs("instance", exist_ok=True)
    
    # Run database setup
    print_status("Running complete database migration...")
    if os.path.exists("database/setup_database.py"):
        if run_quiet([sys.executable, "database/setup_database.py"]):
            print_success("Complete database schema created successfully")
        else:
            print_warning("Complete database schema creation failed, but continuing...")
    else:
        print_warning("Database setup script not found, skipping...")
    
    # Check if database file exists
    if os.path.isfile("instance/site.db"):
        print_status("Database file exists, checking health...")
        try:
            conn = sqlite3.connect("instance/site.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            print_status("Database is healthy and ready")
        except Exception as e:
            print_warning(f"Database health check failed: {e}")
    else:
        print_warning("Database file not found")


def create_default_user() -> None:
    """Create default test user"""
    print_status("Creating default test user...")
    
    try:
        # Check if user already exists
        conn = sqlite3.connect("instance/site.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE email = ?", ("1",))
        if cursor.fetchone():
            print_status("Default test user already exists")
            conn.close()
            return
        
        # Create new user
        password_hash = generate_password_hash("1")
        user_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO user (id, username, email, password_hash, role, is_active, email_verified, 
                            created_at, updated_at, total_lessons, total_notes, total_tasks) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, "1", "1", password_hash, "student", 1, 0, created_at, created_at, 0, 0, 0))
        
        conn.commit()
        conn.close()
        print_success(f"Default test user created: email=1, password=1, id={user_id}")
        
    except Exception as e:
        print_warning(f"Failed to create default user: {e}")


def test_oop_architecture() -> None:
    """Test OOP architecture"""
    print_status("Testing OOP Architecture...")
    
    test_path = os.path.join("scripts", "tests", "test_oop.py")
    if os.path.isfile(test_path):
        print_status("Running OOP architecture test...")
        try:
            subprocess.run([sys.executable, test_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print_success("OOP architecture test passed")
        except subprocess.CalledProcessError:
            print_warning("OOP architecture test failed, but continuing...")
    else:
        print_warning("OOP architecture test not found, skipping...")


def try_port(port: int) -> bool:
    """Check if port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def start_flask_server() -> None:
    """Start Flask development server"""
    print_header("🚀 Starting Smart Learning Hub OOP Architecture Flask Application 🚀")
    
    port = 5003 if try_port(5003) else 5004
    print_status(f"Application will be available at: http://localhost:{port}")
    print_status("Architecture: Clean Architecture + SOLID Principles")
    print_status("Features: User, Lesson, Note, Task, Pomodoro Management")
    print_status("Press Ctrl+C to stop the application")
    
    os.environ["PYTHONPATH"] = os.getcwd()
    
    # Start Flask app
    print_status("Starting Flask development server...")
    print_status(f"Flask will be available at: http://localhost:{port}")
    print_status("Web Interface: http://localhost:{port}")
    print_status("API Endpoints: http://localhost:{port}/api/")
    
    try:
        from app import create_app
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=port)
    except Exception as e:
        print_error(f"Failed to start Flask server: {e}")
        sys.exit(1)


def main() -> None:
    """Main startup function"""
    print_header("Smart Learning Hub - OOP Architecture Environment Setup")
    
    # Setup steps
    reexec_in_venv()
    set_env_defaults()
    ensure_dependencies()
    validate_oop_files()
    setup_database()
    create_default_user()
    test_oop_architecture()
    
    # Start server
    start_flask_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_header("Shutting Down Smart Learning Hub OOP Architecture")
        print_status("Goodbye! 👋")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
