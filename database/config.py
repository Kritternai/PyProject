import os
from pathlib import Path

class DatabaseConfig:
    """Database configuration for Smart Learning Hub"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    INSTANCE_DIR = BASE_DIR / 'instance'
    DATABASE_PATH = INSTANCE_DIR / 'site.db'
    
    # Database URL
    SQLITE_URL = f'sqlite:///{DATABASE_PATH}'
    
    # Migration settings
    MIGRATION_DIR = BASE_DIR / 'database' / 'migrations'
    SCHEMA_DIR = BASE_DIR / 'database' / 'schemas'
    BACKUP_DIR = BASE_DIR / 'database' / 'backups'
    
    # Database settings
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600
    
    # Backup settings
    BACKUP_RETENTION_DAYS = 30
    AUTO_BACKUP = True
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist"""
        cls.INSTANCE_DIR.mkdir(exist_ok=True)
        cls.MIGRATION_DIR.mkdir(exist_ok=True)
        cls.SCHEMA_DIR.mkdir(exist_ok=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_database_url(cls):
        """Get database URL based on environment"""
        return cls.SQLITE_URL
