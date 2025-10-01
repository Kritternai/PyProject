#!/usr/bin/env python3
"""
Database Initialization Script for Smart Learning Hub
This script creates all database tables and initializes the database system.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('database_init.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main database initialization function"""
    try:
        logger.info("Starting database initialization...")
        
        # Import database components
        from database import init_database, get_db_manager
        
        # Initialize database
        logger.info("Creating database tables...")
        success = init_database()
        
        if success:
            logger.info("Database initialization completed successfully!")
            
            # Get database info
            manager = get_db_manager()
            info = manager.get_database_info()
            
            logger.info("Database Information:")
            logger.info(f"  Path: {info.get('database_path', 'N/A')}")
            logger.info(f"  Size: {info.get('database_size_mb', 0)} MB")
            logger.info(f"  Tables: {info.get('table_count', 0)}")
            logger.info(f"  Health: {info.get('health_status', 'N/A')}")
            
            if info.get('tables'):
                logger.info("  Table List:")
                for table in info['tables']:
                    logger.info(f"    - {table}")
            
        else:
            logger.error("Database initialization failed!")
            return 1
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required packages are installed")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
