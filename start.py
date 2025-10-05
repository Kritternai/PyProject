import os
import sys
import subprocess
import venv
import socket
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
    if not os.environ.get("GOOGLE_CLIENT_ID") or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        print_warning("Google OAuth credentials not found. Using development defaults.")
        os.environ.setdefault("GOOGLE_CLIENT_ID", "231151462337-sspbadu0r8rlnoht5pgg77un10i26r8d.apps.googleusercontent.com")
        os.environ.setdefault("GOOGLE_CLIENT_SECRET", "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")
        os.environ.setdefault("FLASK_SECRET_KEY", "your_strong_random_flask_secret_key")
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("FLASK_DEBUG", "1")


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check)


def run_quiet(cmd: List[str]) -> bool:
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def ensure_dependencies() -> None:
    print_status("Checking Python dependencies...")
    if os.path.isfile("requirements.txt"):
        if not run_quiet([sys.executable, "-c", "import flask"]):
            print_warning("Flask not found, installing dependencies...")
            run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]) 
        if not run_quiet([sys.executable, "-c", "import dependency_injector"]):
            print_warning("dependency-injector not found, installing...")
            run([sys.executable, "-m", "pip", "install", "dependency-injector"]) 
    else:
        print_warning("requirements.txt not found, installing basic dependencies...")
        run([sys.executable, "-m", "pip", "install", "flask", "sqlalchemy", "werkzeug", "dependency-injector"]) 


def validate_oop_files() -> None:
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


def init_database() -> None:
    print_status("Initializing database...")
    os.makedirs("instance", exist_ok=True)

    code_health = (
        "from app import create_app, db\n"
        "from app.infrastructure.di.container import configure_services\n"
        "app = create_app()\n"
        "configure_services()\n"
        "from sqlalchemy import text\n"
        "with app.app_context():\n"
        "    db.session.execute(text('SELECT 1'))\n"
    )

    code_create = (
        "from app import create_app, db\n"
        "from app.infrastructure.di.container import configure_services\n"
        "app = create_app()\n"
        "configure_services()\n"
        "with app.app_context():\n"
        "    db.create_all()\n"
        "    print('Database created successfully')\n"
    )

    def py_ok(snippet: str) -> bool:
        return run_quiet([sys.executable, "-c", snippet])

    db_path = os.path.join("instance", "site.db")
    if os.path.isfile(db_path):
        print_status("Database file exists, checking health...")
        if not py_ok(code_health):
            print_warning("Database health check failed, reinitializing...")
            run([sys.executable, "-c", code_create])
        else:
            print_status("Database is healthy and ready")
    else:
        print_status("Database file not found, creating new database...")
        run([sys.executable, "-c", code_create])


def create_default_user() -> None:
    print_status("Creating default test user...")
    snippet = (
        "import sys\n"
        "from werkzeug.security import generate_password_hash\n"
        "import uuid\n"
        "from datetime import datetime\n"
        "from app import create_app, db\n"
        "from app.infrastructure.di.container import get_service\n"
        "from app.domain.interfaces.services.user_service import UserService\n"
        "from app.domain.value_objects.email import Email\n"
        "from app.domain.value_objects.password import Password\n"
        "app = create_app()\n"
        "with app.app_context():\n"
        "    try:\n"
        "        user_service = get_service(UserService)\n"
        "        from app.domain.interfaces.repositories.user_repository import UserRepository\n"
        "        user_repo = get_service(UserRepository)\n"
        "        existing = user_repo.get_by_email(Email('1'))\n"
        "        if existing:\n"
        "            print('Default test user already exists')\n"
        "        else:\n"
        "            email = Email('1')\n"
        "            password = Password('1')\n"
        "            user = user_service.create_user(email=email, password=password, username='user1')\n"
        "            print(f'Default test user created: email=1, password=1, username=user1, id={user.id}')\n"
        "    except Exception:\n"
        "        import sqlite3, traceback\n"
        "        print('OOP creation failed, using SQL fallback...')\n"
        "        password_hash = generate_password_hash('1')\n"
        "        user_id = str(uuid.uuid4())\n"
        "        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')\n"
        "        conn = sqlite3.connect('instance/site.db')\n"
        "        cur = conn.cursor()\n"
        "        cur.execute('SELECT id FROM user WHERE email = ?', ('1',))\n"
        "        if cur.fetchone():\n"
        "            print('Default test user already exists')\n"
        "        else:\n"
        "            cur.execute(\n"
        "                'INSERT INTO user (id, username, email, password_hash, role, is_active, email_verified, created_at, updated_at, total_lessons, total_notes, total_tasks) ' \
"
        "                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',\n"
        "                (user_id, '1', '1', password_hash, 'student', 1, 0, created_at, created_at, 0, 0, 0)\n"
        "            )\n"
        "            conn.commit()\n"
        "            print(f'Default test user created via SQL: email=1, password=1, id={user_id}')\n"
        "        conn.close()\n"
    )
    run([sys.executable, "-c", snippet])


def files_exist(paths: List[str]) -> None:
    for p in paths:
        if not os.path.isfile(p):
            print_error(f"Required file not found: {p}")
            sys.exit(1)


def try_port(port: int) -> bool:
    import socket as _socket
    with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def maybe_run_oop_test() -> None:
    test_path = os.path.join("scripts", "tests", "test_oop.py")
    if os.path.isfile(test_path):
        print_status("Running OOP architecture test...")
        try:
            subprocess.run([sys.executable, test_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print_success("OOP architecture test passed")
        except subprocess.CalledProcessError:
            print_warning("OOP architecture test failed, but continuing...")
    else:
        print_warning("scripts/tests/test_oop.py not found, skipping OOP test")


def start_app() -> None:
    print_header("🚀 Starting Smart Learning Hub OOP Architecture Flask Application 🚀")
    port = 5003 if try_port(5003) else 5004
    print_status(f"Application will be available at: http://localhost:{port}")
    print_status("Architecture: Clean Architecture + SOLID Principles")
    print_status("Features: User, Lesson, Note, Task Management")
    print_status("Press Ctrl+C to stop the application")
    os.environ["PYTHONPATH"] = os.getcwd()

    snippet = (
        "from app import create_app, db\n"
        "app = create_app()\n"
        "from app.infrastructure.di.container import configure_services\n"
        "configure_services()\n"
        "with app.app_context():\n"
        "    db.create_all()\n"
        f"app.run(debug=True, host='0.0.0.0', port={port})\n"
    )
    run([sys.executable, "-c", snippet])


def final_arch_check() -> None:
    snippet = (
        "from app import create_app\n"
        "from app.infrastructure.di.container import configure_services\n"
        "app = create_app()\n"
        "configure_services()\n"
        "print('OOP architecture is healthy')\n"
    )
    if not run_quiet([sys.executable, "-c", snippet]):
        print_error("Final OOP architecture check failed")
        sys.exit(1)


def main() -> None:
    print_header("Smart Learning Hub - OOP Architecture Environment Setup")
    reexec_in_venv()
    set_env_defaults()
    ensure_dependencies()
    validate_oop_files()
    init_database()
    create_default_user()
    files_exist(["scripts/run_new.py", "app/__init__.py", "app/infrastructure/di/container.py"])
    final_arch_check()
    maybe_run_oop_test()
    start_app()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_header("Shutting Down Smart Learning Hub OOP Architecture")
        print_status("Goodbye! 👋")
