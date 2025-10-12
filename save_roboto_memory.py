
#!/usr/bin/env python3
"""
💾 Roboto Memory Save Script
Saves all of Roboto's current memory with San Antonio timestamp
"""

import json
from datetime import datetime
import pytz
from app_enhanced import get_user_roberto, save_user_data
from comprehensive_memory_system import create_all_backups
from san_antonio_realtime_system import get_san_antonio_time

def save_roboto_memory():
    """Save Roboto's complete memory state with timestamp"""
    
    # Get San Antonio time
    sa_time = get_san_antonio_time()
    
    print("💾 Saving Roboto's Memory...")
    print(f"📅 {sa_time['formatted']}")
    print("-" * 50)
    
    # Get Roboto instance
    roberto = get_user_roberto()
    
    # Save through all systems
    save_user_data()
    
    # Create comprehensive backups
    backup_files = create_all_backups(roberto)
    
    # Create timestamped summary
    summary = {
        "save_timestamp": sa_time['current_datetime']['timestamp'],
        "save_time_formatted": sa_time['formatted'],
        "location": "San Antonio, Texas",
        "total_conversations": len(roberto.chat_history),
        "current_emotion": roberto.current_emotion,
        "current_user": roberto.current_user,
        "backup_files_created": len(backup_files),
        "memory_systems": {
            "chat_history": len(roberto.chat_history),
            "learned_patterns": len(roberto.learned_patterns),
            "user_preferences": len(roberto.user_preferences),
            "permanent_memories": len(roberto.permanent_roberto_memory.permanent_memories) if hasattr(roberto, 'permanent_roberto_memory') else 0
        }
    }
    
    # Save summary
    summary_file = f"memory_save_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Memory save complete!")
    print(f"📁 Backup files created: {len(backup_files)}")
    print(f"💬 Total conversations: {summary['memory_systems']['chat_history']}")
    print(f"🧠 Learned patterns: {summary['memory_systems']['learned_patterns']}")
    print(f"🔐 Permanent memories: {summary['memory_systems']['permanent_memories']}")
    print(f"📊 Summary saved to: {summary_file}")
    
    return summary

if __name__ == "__main__":
    save_roboto_memory()
