import os
import sys
import pytest

# Ensure project root is on sys.path so `app` can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Pre-set env to avoid ProductionConfig import checks
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("FLASK_SECRET_KEY", "x" * 64)
TEST_DB_PATH = os.path.join(PROJECT_ROOT, "test_data.sqlite")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")

from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    # Ensure testing config is used
    os.environ.setdefault("FLASK_ENV", "testing")
    # Use development config to avoid SQLAlchemy engine option incompatibilities
    application = create_app("development")
    return application


@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        # Ensure all models are registered before creating tables
        from app import import_models as _import_core_models
        _import_core_models()
        # Explicitly import Pomodoro models (not included in import_models)
        from app.models import pomodoro_session, pomodoro_statistics  # noqa: F401
        _db.create_all()
        try:
            yield _db
        finally:
            _db.drop_all()


@pytest.fixture()
def session(app, db):
    # Provide a clean transaction for each test
    ctx = app.app_context()
    ctx.push()
    try:
        yield db.session
        db.session.rollback()
    finally:
        ctx.pop()


@pytest.fixture()
def user(session):
    # Minimal user factory for FK integrity
    from app.models.user import UserModel
    import uuid

    u = UserModel(
        username=f"tester_{uuid.uuid4().hex[:8]}",
        email=f"tester_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="x" * 80,
    )
    session.add(u)
    session.commit()
    return u
