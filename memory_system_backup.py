
"""
Memory System Backup - Additional storage layer for Roboto SAI
Created by Roberto Villarreal Martinez
"""

import json
import os
from datetime import datetime
from pathlib import Path

class MemorySystemBackup:
    """Enhanced backup system with multiple storage layers"""
    
    def __init__(self):
        self.backup_dirs = {
            "primary": "memory_storage_primary",
            "secondary": "memory_storage_secondary",
            "archive": "memory_storage_archive",
            "emergency": "memory_storage_emergency",
            "daily": "memory_storage_daily"
        }
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Create all backup directories"""
        for dir_name in self.backup_dirs.values():
            os.makedirs(dir_name, exist_ok=True)
    
    def create_backup_snapshot(self, roboto_instance, backup_type="primary"):
        """Create a complete memory snapshot"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_dirs.get(backup_type, "primary")
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "backup_type": backup_type,
            "chat_history": getattr(roboto_instance, 'chat_history', []),
            "learned_patterns": getattr(roboto_instance, 'learned_patterns', {}),
            "user_preferences": getattr(roboto_instance, 'user_preferences', {}),
            "current_emotion": str(getattr(roboto_instance, 'current_emotion', 'curious')),
            "system_version": "1.0"
        }
        
        filepath = os.path.join(backup_dir, f"snapshot_{timestamp}.json")
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        return filepath
    
    def create_daily_backup(self, roboto_instance):
        """Create daily backup with rotation"""
        date_str = datetime.now().strftime('%Y%m%d')
        filepath = os.path.join(self.backup_dirs['daily'], f"daily_backup_{date_str}.json")
        
        backup_data = {
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
            "chat_count": len(getattr(roboto_instance, 'chat_history', [])),
            "pattern_count": len(getattr(roboto_instance, 'learned_patterns', {})),
            "full_data": {
                "chat_history": getattr(roboto_instance, 'chat_history', []),
                "learned_patterns": getattr(roboto_instance, 'learned_patterns', {}),
                "user_preferences": getattr(roboto_instance, 'user_preferences', {})
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        self._cleanup_old_daily_backups()
        return filepath
    
    def _cleanup_old_daily_backups(self, keep_days=30):
        """Keep only recent daily backups"""
        daily_dir = self.backup_dirs['daily']
        files = sorted(Path(daily_dir).glob("daily_backup_*.json"))
        
        if len(files) > keep_days:
            for old_file in files[:-keep_days]:
                old_file.unlink()

# Global instance
MEMORY_BACKUP_SYSTEM = MemorySystemBackup()

def create_memory_backup(roboto_instance, backup_type="primary"):
    """Factory function for creating backups"""
    return MEMORY_BACKUP_SYSTEM.create_backup_snapshot(roboto_instance, backup_type)
