from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging
from pathlib import Path
from .config import DatabaseConfig
from .models import Base
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for Smart Learning Hub"""
    
    def __init__(self, config=None):
        self.config = config or DatabaseConfig()
        self.engine = None
        self.session_factory = None
        self.Session = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup database engine with proper configuration"""
        try:
            # Ensure directories exist
            self.config.ensure_directories()
            
            # Create engine
            if self.config.get_database_url().startswith('sqlite'):
                # SQLite configuration
                self.engine = create_engine(
                    self.config.get_database_url(),
                    connect_args={'check_same_thread': False},
                    poolclass=QueuePool,
                    pool_size=self.config.POOL_SIZE,
                    max_overflow=self.config.MAX_OVERFLOW,
                    pool_timeout=self.config.POOL_TIMEOUT,
                    pool_recycle=self.config.POOL_RECYCLE,
                    echo=False  # Set to True for SQL debugging
                )
                
                # Enable foreign key support for SQLite
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA cache_size=10000")
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    cursor.close()
                    
            else:
                # PostgreSQL configuration
                self.engine = create_engine(
                    self.config.get_database_url(),
                    poolclass=QueuePool,
                    pool_size=self.config.POOL_SIZE,
                    max_overflow=self.config.MAX_OVERFLOW,
                    pool_timeout=self.config.POOL_TIMEOUT,
                    pool_recycle=self.config.POOL_RECYCLE,
                    echo=False
                )
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            logger.info("Database engine setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup database engine: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("All database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def drop_tables(self):
        """Drop all database tables (DANGEROUS!)"""
        try:
            Base.metadata.drop_all(self.engine)
            logger.warning("All database tables dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            return False
    
    def reset_database(self):
        """Reset database by dropping and recreating all tables"""
        try:
            logger.warning("Resetting database...")
            self.drop_tables()
            self.create_tables()
            logger.info("Database reset completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
    
    def health_check(self):
        """Check database health"""
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_database_info(self):
        """Get database information"""
        try:
            db_path = Path(self.config.DATABASE_PATH)
            if db_path.exists():
                return {
                    'database_path': str(db_path),
                    'database_size': db_path.stat().st_size,
                    'database_size_mb': round(db_path.stat().st_size / (1024 * 1024), 2),
                    'tables': [table.name for table in Base.metadata.sorted_tables],
                    'table_count': len(Base.metadata.sorted_tables),
                    'health_status': 'healthy' if self.health_check() else 'unhealthy'
                }
            else:
                return {
                    'database_path': str(db_path),
                    'database_size': 0,
                    'database_size_mb': 0,
                    'tables': [],
                    'table_count': 0,
                    'health_status': 'not_created'
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {'error': str(e)}
    
    def backup_database(self, backup_path=None):
        """Create database backup"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.config.BACKUP_DIR / f"backup_{timestamp}.db"
            
            # For SQLite, just copy the file
            import shutil
            shutil.copy2(self.config.DATABASE_PATH, backup_path)
            
            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return None
    
    def close(self):
        """Close database connections"""
        try:
            if self.Session:
                self.Session.remove()
            if self.engine:
                self.engine.dispose()
            logger.info("Database connections closed successfully")
        except Exception as e:
            logger.error(f"Failed to close database connections: {e}")

# Global database manager instance
db_manager = None

def get_db_manager():
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_database():
    """Initialize database with tables"""
    manager = get_db_manager()
    return manager.create_tables()

def close_database():
    """Close database connections"""
    global db_manager
    if db_manager:
        db_manager.close()
        db_manager = None
