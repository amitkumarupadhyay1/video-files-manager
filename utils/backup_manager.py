import shutil
import os
import sqlite3
from datetime import datetime
import glob
from config import DATABASE_PATH

class BackupManager:
    """Manages database backups"""
    
    def __init__(self, backup_dir="storage/backups", max_backups=10):
        self.db_path = DATABASE_PATH
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        
        # Ensure backup directory exists
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def create_backup(self, manual=False):
        """Create a backup of the database"""
        if not os.path.exists(self.db_path):
            return False, "Database file not found"
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "manual_" if manual else "auto_"
            backup_filename = f"video_manager_{prefix}{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Perform backup using SQLite API to ensure integrity
            # (better than file copy for active databases)
            src = sqlite3.connect(self.db_path)
            dst = sqlite3.connect(backup_path)
            with dst:
                src.backup(dst)
            dst.close()
            src.close()
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return True, f"Backup created: {backup_filename}"
        except Exception as e:
            return False, str(e)
            
    def _cleanup_old_backups(self):
        """Keep only the latest max_backups files"""
        try:
            # Get all .db files in backup dir
            files = glob.glob(os.path.join(self.backup_dir, "*.db"))
            # Sort by modification time (newest last)
            files.sort(key=os.path.getmtime)
            
            # Remove oldest if exceeded limit
            while len(files) > self.max_backups:
                oldest_file = files.pop(0)
                os.remove(oldest_file)
        except Exception:
            pass # Fail silently on cleanup
