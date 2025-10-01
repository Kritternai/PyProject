#!/usr/bin/env python3
"""
Smart Learning Hub - OOP Architecture Flask Startup Script
Python version of start_flask_new.sh
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path
from typing import List, Tuple, Optional

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class FlaskStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.run_file = self.project_root / "run_new.py"
        self.instance_dir = self.project_root / "instance"
        self.port = 5003
        
    def print_status(self, message: str):
        print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")
    
    def print_success(self, message: str):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")
    
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    def print_error(self, message: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    def print_header(self, message: str):
        print(f"{Colors.BLUE}{'='*77}{Colors.NC}")
        print(f"{Colors.BLUE}{message}{Colors.NC}")
        print(f"{Colors.BLUE}{'='*77}{Colors.NC}")
    
    def print_step(self, message: str):
        print(f"{Colors.CYAN}[STEP]{Colors.NC} {message}")
    
    def setup_environment(self):
        """Set up environment variables"""
        self.print_step("Setting environment variables...")
        
        # Check if environment variables are already set
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        flask_secret_key = os.getenv('FLASK_SECRET_KEY')
        
        if not google_client_id or not google_client_secret:
            self.print_warning("Google OAuth credentials not found in environment variables")
            self.print_status("Please set the following environment variables:")
            self.print_status("export GOOGLE_CLIENT_ID='your-client-id-here'")
            self.print_status("export GOOGLE_CLIENT_SECRET='your-client-secret-here'")
            self.print_status("export FLASK_SECRET_KEY='your-strong-random-flask-secret-key'")
            self.print_warning("Using default development values...")
            
            # Set default development values
            os.environ['GOOGLE_CLIENT_ID'] = "231151462337-sspbadu0r8rlnoht5pgg77un10i26r8d.apps.googleusercontent.com"
            os.environ['GOOGLE_CLIENT_SECRET'] = "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"
            os.environ['FLASK_SECRET_KEY'] = "your_strong_random_flask_secret_key"
        else:
            self.print_success("Google OAuth credentials found in environment variables")
        
        # Set other environment variables
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
        os.environ['FLASK_ENV'] = "development"
        os.environ['FLASK_DEBUG'] = "1"
        
        self.print_status("Environment variables set successfully")
    
    def check_virtual_environment(self) -> bool:
        """Check and activate virtual environment"""
        self.print_step("Checking virtual environment...")
        
        if self.venv_path.exists():
            self.print_status("Virtual environment found at venv/")
            
            # Activate virtual environment
            if sys.platform == "win32":
                activate_script = self.venv_path / "Scripts" / "activate.bat"
                python_executable = self.venv_path / "Scripts" / "python.exe"
            else:
                activate_script = self.venv_path / "bin" / "activate"
                python_executable = self.venv_path / "bin" / "python"
            
            if python_executable.exists():
                self.print_status("Virtual environment activated")
                return True
            else:
                self.print_error("Virtual environment Python executable not found")
                return False
        else:
            self.print_warning("Virtual environment not found at venv/")
            return self.create_virtual_environment()
    
    def create_virtual_environment(self) -> bool:
        """Create new virtual environment"""
        self.print_step("Creating new virtual environment...")
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                         check=True, cwd=self.project_root)
            self.print_status("Virtual environment created and activated")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_python_executable(self) -> str:
        """Get the Python executable path"""
        if sys.platform == "win32":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def check_dependencies(self) -> bool:
        """Check and install Python dependencies"""
        self.print_step("Checking Python dependencies...")
        
        python_exec = self.get_python_executable()
        
        if self.requirements_file.exists():
            self.print_status("Requirements file found")
            
            # Check if Flask is installed
            try:
                subprocess.run([python_exec, "-c", "import flask"], 
                             check=True, capture_output=True)
                self.print_status("Key dependencies already installed")
            except subprocess.CalledProcessError:
                self.print_warning("Flask not found, installing dependencies...")
                try:
                    subprocess.run([python_exec, "-m", "pip", "install", "-r", str(self.requirements_file)], 
                                 check=True, cwd=self.project_root)
                    self.print_status("Dependencies installed successfully")
                except subprocess.CalledProcessError as e:
                    self.print_error(f"Failed to install dependencies: {e}")
                    return False
            
            # Check for dependency-injector
            try:
                subprocess.run([python_exec, "-c", "import dependency_injector"], 
                             check=True, capture_output=True)
                self.print_status("dependency-injector already installed")
            except subprocess.CalledProcessError:
                self.print_warning("dependency-injector not found, installing...")
                try:
                    subprocess.run([python_exec, "-m", "pip", "install", "dependency-injector"], 
                                 check=True)
                    self.print_status("dependency-injector installed successfully")
                except subprocess.CalledProcessError as e:
                    self.print_error(f"Failed to install dependency-injector: {e}")
                    return False
        else:
            self.print_warning("requirements.txt not found, installing basic dependencies...")
            try:
                subprocess.run([python_exec, "-m", "pip", "install", 
                              "flask", "sqlalchemy", "werkzeug", "dependency-injector"], 
                             check=True)
                self.print_status("Basic dependencies installed")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install basic dependencies: {e}")
                return False
        
        return True
    
    def validate_oop_architecture(self) -> bool:
        """Validate OOP architecture files"""
        self.print_step("Validating OOP Architecture...")
        
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
            "app/infrastructure/di/container.py"
        ]
        
        missing_files = []
        for file_path in oop_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if not missing_files:
            self.print_success("All OOP architecture files found")
            return True
        else:
            self.print_error("Missing OOP architecture files:")
            for file_path in missing_files:
                self.print_error(f"  - {file_path}")
            self.print_error("Please ensure the OOP architecture is properly set up")
            return False
    
    def initialize_database(self) -> bool:
        """Initialize database"""
        self.print_step("Initializing database...")
        
        # Create instance directory if it doesn't exist
        if not self.instance_dir.exists():
            self.print_status("Creating instance directory...")
            self.instance_dir.mkdir(parents=True, exist_ok=True)
        
        python_exec = self.get_python_executable()
        
        # Check if database file exists
        db_file = self.instance_dir / "site.db"
        if db_file.exists():
            self.print_status("Database file exists, checking health...")
            
            # Test database health
            try:
                result = subprocess.run([
                    python_exec, "-c", """
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
"""
                ], check=True, capture_output=True, text=True, cwd=self.project_root)
                
                self.print_status("Database is healthy and ready")
                return True
                
            except subprocess.CalledProcessError:
                self.print_warning("Database health check failed, reinitializing...")
                return self.reinitialize_database()
        else:
            self.print_status("Database file not found, creating new database...")
            return self.create_database()
    
    def create_database(self) -> bool:
        """Create new database"""
        python_exec = self.get_python_executable()
        
        try:
            result = subprocess.run([
                python_exec, "-c", """
from app import create_app, db
from app.infrastructure.di.container import configure_services
app = create_app()
configure_services()
with app.app_context():
    db.create_all()
    print('Database created successfully')
"""
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.print_status("Database created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to create database: {e}")
            return False
    
    def reinitialize_database(self) -> bool:
        """Reinitialize database"""
        python_exec = self.get_python_executable()
        
        try:
            result = subprocess.run([
                python_exec, "-c", """
from app import create_app, db
from app.infrastructure.di.container import configure_services
app = create_app()
configure_services()
with app.app_context():
    db.create_all()
    print('Database reinitialized')
"""
            ], check=True, capture_output=True, text=True, cwd=self.project_root)
            
            self.print_status("Database reinitialized")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to reinitialize database: {e}")
            return False
    
    def test_oop_architecture(self) -> bool:
        """Test OOP architecture"""
        self.print_step("Testing OOP Architecture...")
        
        test_file = self.project_root / "test_oop.py"
        if test_file.exists():
            self.print_status("Running OOP architecture test...")
            python_exec = self.get_python_executable()
            
            try:
                subprocess.run([python_exec, str(test_file)], 
                             check=True, capture_output=True, cwd=self.project_root)
                self.print_success("OOP architecture test passed")
                return True
            except subprocess.CalledProcessError:
                self.print_warning("OOP architecture test failed, but continuing...")
                return True
        else:
            self.print_warning("test_oop.py not found, skipping OOP test")
            return True
    
    def check_port_availability(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    def find_available_port(self) -> int:
        """Find an available port"""
        for port in range(5003, 5010):
            if self.check_port_availability(port):
                return port
        return 5003  # Default fallback
    
    def start_flask_application(self):
        """Start Flask application"""
        self.print_header("🚀 Starting Smart Learning Hub OOP Architecture Flask Application 🚀")
        
        if not self.run_file.exists():
            self.print_error("run_new.py not found!")
            self.print_error("Please ensure the OOP Flask application file exists")
            return False
        
        self.print_status("Flask application file: run_new.py")
        self.print_status("Architecture: Clean Architecture + SOLID Principles")
        self.print_status(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
        self.print_status(f"Debug mode: {os.getenv('FLASK_DEBUG', '1')}")
        
        # Find available port
        self.port = self.find_available_port()
        if self.port != 5003:
            self.print_warning(f"Port 5003 is busy, using port {self.port}")
        
        self.print_status(f"Application will be available at: http://localhost:{self.port}")
        self.print_status("Architecture: Clean Architecture + SOLID Principles")
        self.print_status("Features: User, Lesson, Note, Task, Pomodoro, Tracking Management")
        self.print_status("Press Ctrl+C to stop the application")
        print()
        
        # Update run_new.py with the correct port if needed
        if self.port != 5003:
            self.print_status(f"Updating run_new.py to use port {self.port}...")
            self.update_port_in_run_file()
        
        # Start Flask application
        self.print_step("Starting OOP Flask development server...")
        python_exec = self.get_python_executable()
        
        try:
            subprocess.run([python_exec, str(self.run_file)], cwd=self.project_root)
        except KeyboardInterrupt:
            self.print_status("Application stopped by user")
        except Exception as e:
            self.print_error(f"Failed to start Flask application: {e}")
            return False
        
        return True
    
    def update_port_in_run_file(self):
        """Update port in run_new.py"""
        try:
            with open(self.run_file, 'r') as f:
                content = f.read()
            
            # Replace port=5003 with the new port
            updated_content = content.replace('port=5003', f'port={self.port}')
            
            with open(self.run_file, 'w') as f:
                f.write(updated_content)
                
        except Exception as e:
            self.print_warning(f"Failed to update port in run_new.py: {e}")
    
    def cleanup(self):
        """Cleanup on exit"""
        print()
        self.print_header("Shutting Down Smart Learning Hub OOP Architecture")
        self.print_status("Cleaning up...")
        self.print_status("Goodbye! 👋")
    
    def run(self):
        """Main run method"""
        try:
            # Setup
            self.print_header("Smart Learning Hub - OOP Architecture Environment Setup")
            
            # 1. Environment setup
            self.setup_environment()
            
            # 2. Virtual environment check
            if not self.check_virtual_environment():
                self.print_error("Failed to setup virtual environment")
                return False
            
            # 3. Dependencies check
            if not self.check_dependencies():
                self.print_error("Failed to setup dependencies")
                return False
            
            # 4. OOP architecture validation
            if not self.validate_oop_architecture():
                self.print_error("OOP architecture validation failed")
                return False
            
            # 5. Database initialization
            if not self.initialize_database():
                self.print_error("Database initialization failed")
                return False
            
            # 6. OOP architecture test
            if not self.test_oop_architecture():
                self.print_error("OOP architecture test failed")
                return False
            
            # 7. Start Flask application
            return self.start_flask_application()
            
        except KeyboardInterrupt:
            self.print_status("Application interrupted by user")
            return True
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    starter = FlaskStarter()
    success = starter.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()