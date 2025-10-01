"""
Database Backup Service
Handles automatic database backups
"""

import sqlite3
import os
import shutil
from datetime import datetime
import json

class BackupService:
    @staticmethod
    def create_backup():
        """
        Create a backup of the database
        """
        db_path = 'instance/site.db'
        backup_dir = 'backups'
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'{backup_dir}/site_backup_{timestamp}.db'
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✓ Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    @staticmethod
    def get_backup_info():
        """
        Get information about existing backups
        """
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for file in os.listdir(backup_dir):
            if file.startswith('site_backup_') and file.endswith('.db'):
                file_path = os.path.join(backup_dir, file)
                stat = os.stat(file_path)
                backups.append({
                    'filename': file,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'path': file_path
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    @staticmethod
    def cleanup_old_backups(keep_count=5):
        """
        Clean up old backups, keeping only the most recent ones
        """
        backups = BackupService.get_backup_info()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                try:
                    os.remove(backup['path'])
                    print(f"✓ Removed old backup: {backup['filename']}")
                except Exception as e:
                    print(f"❌ Failed to remove backup {backup['filename']}: {e}")
    
    @staticmethod
    def restore_backup(backup_path):
        """
        Restore database from backup
        """
        db_path = 'instance/site.db'
        
        try:
            # Create backup of current database before restore
            current_backup = BackupService.create_backup()
            
            # Restore from backup
            shutil.copy2(backup_path, db_path)
            print(f"✓ Database restored from: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False 