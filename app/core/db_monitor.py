"""
Database Monitoring Service
Monitors database health and performance
"""

import sqlite3
import os
from datetime import datetime
import json

class DatabaseMonitor:
    @staticmethod
    def get_database_stats():
        """
        Get comprehensive database statistics
        """
        db_path = 'instance/site.db'
        
        if not os.path.exists(db_path):
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Get table sizes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            stats = {
                'database_size': os.path.getsize(db_path),
                'tables': {},
                'total_records': 0,
                'last_updated': datetime.now().isoformat()
            }
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats['tables'][table_name] = count
                stats['total_records'] += count
            
            # Get Google Classroom specific stats
            cursor.execute("SELECT COUNT(*) FROM lesson WHERE source_platform = 'google_classroom'")
            gc_lessons = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM imported_data WHERE platform = 'google_classroom_api'")
            gc_data = cursor.fetchone()[0]
            
            stats['google_classroom'] = {
                'lessons': gc_lessons,
                'imported_data': gc_data
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def check_database_integrity():
        """
        Check database integrity
        """
        db_path = 'instance/site.db'
        
        if not os.path.exists(db_path):
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] == 'ok':
                return True
            else:
                print(f"Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            print(f"Error checking database integrity: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def optimize_database():
        """
        Optimize database performance
        """
        db_path = 'instance/site.db'
        
        if not os.path.exists(db_path):
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Run VACUUM to optimize database
            cursor.execute("VACUUM")
            
            # Update statistics
            cursor.execute("ANALYZE")
            
            conn.commit()
            print("✓ Database optimized successfully")
            return True
            
        except Exception as e:
            print(f"Error optimizing database: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_performance_metrics():
        """
        Get database performance metrics
        """
        db_path = 'instance/site.db'
        
        if not os.path.exists(db_path):
            return None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            metrics = {}
            
            # Check index usage
            cursor.execute("PRAGMA index_list(lesson)")
            lesson_indexes = cursor.fetchall()
            metrics['lesson_indexes'] = len(lesson_indexes)
            
            # Check cache size
            cursor.execute("PRAGMA cache_size")
            cache_size = cursor.fetchone()[0]
            metrics['cache_size'] = cache_size
            
            # Check page count
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            metrics['page_count'] = page_count
            
            return metrics
            
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return None
        finally:
            conn.close() 