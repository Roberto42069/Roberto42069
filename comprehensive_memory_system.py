import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, List
import shutil

class ComprehensiveMemorySystem:
    """
    Enhanced memory system that creates multiple backup files and ensures
    Roberto Villarreal Martinez is never forgotten
    """

    def __init__(self):
        self.memory_directories = [
            "memory_backups",
            "conversation_archives",
            "emotional_snapshots",
            "learning_checkpoints",
            "user_profiles_backup"
        ]
        self.ensure_directories()

    def ensure_directories(self):
        """Create all memory backup directories"""
        for directory in self.memory_directories:
            os.makedirs(directory, exist_ok=True)

    def create_comprehensive_backup(self, roboto_instance):
        """Create multiple backup files across different systems with timeout protection"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backups_created = []

        # Prioritize critical backups first
        backup_tasks = [
            ("Roberto memory", lambda: self.backup_roberto_memory(roboto_instance, timestamp)),
            ("Main memory", lambda: self.backup_main_memory(roboto_instance, timestamp)),
            ("User profiles", lambda: self.backup_user_profiles(roboto_instance, timestamp)),
            ("Emotional state", lambda: self.backup_emotional_state(roboto_instance, timestamp)),
            ("Learning patterns", lambda: self.backup_learning_patterns(roboto_instance, timestamp)),
            ("Conversations", lambda: self.backup_conversations(roboto_instance, timestamp)),
        ]

        for name, backup_fn in backup_tasks:
            try:
                backup_file = backup_fn()
                if backup_file:
                    backups_created.append(backup_file)
            except Exception as e:
                print(f"{name} backup failed: {e}")
                continue

        return backups_created

    def _serialize_for_json(self, obj):
        """Convert non-serializable objects to JSON-compatible format"""
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Handle custom objects
            return str(obj)
        return obj

    def backup_main_memory(self, roboto, timestamp):
        """Backup main memory data"""
        try:
            filepath = f"memory_backups/main_memory_{timestamp}.json"

            # Limit chat history to prevent timeout
            chat_history = getattr(roboto, 'chat_history', [])
            limited_history = chat_history[-100:] if len(chat_history) > 100 else chat_history

            memory_data = {
                "timestamp": datetime.now().isoformat(),
                "chat_history_count": len(chat_history),
                "chat_history": self._serialize_for_json(limited_history),
                "learned_patterns": self._serialize_for_json(getattr(roboto, 'learned_patterns', {})),
                "user_preferences": self._serialize_for_json(getattr(roboto, 'user_preferences', {})),
                "current_emotion": str(getattr(roboto, 'current_emotion', 'curious')),
                "current_user": str(getattr(roboto, 'current_user', None)) if getattr(roboto, 'current_user', None) else None
            }

            # Use faster serialization without indent for large data
            with open(filepath, 'w') as f:
                json.dump(memory_data, f, default=str, ensure_ascii=False)

            return filepath
        except Exception as e:
            print(f"Main memory backup error: {e}")
            # Try minimal backup
            try:
                minimal_data = {
                    "timestamp": datetime.now().isoformat(),
                    "current_user": str(getattr(roboto, 'current_user', None)),
                    "backup_status": "partial_failure"
                }
                with open(filepath, 'w') as f:
                    json.dump(minimal_data, f)
                return filepath
            except:
                return None

    def backup_conversations(self, roboto, timestamp):
        """Backup all conversations (limited to recent)"""
        try:
            filepath = f"conversation_archives/conversations_{timestamp}.json"

            chat_history = getattr(roboto, 'chat_history', [])
            # Only backup last 50 conversations to prevent timeout
            recent_conversations = chat_history[-50:] if len(chat_history) > 50 else chat_history

            conversations = {
                "timestamp": datetime.now().isoformat(),
                "total_conversations": len(chat_history),
                "recent_conversations": recent_conversations
            }

            with open(filepath, 'w') as f:
                json.dump(conversations, f, default=str, ensure_ascii=False)

            return filepath
        except Exception as e:
            print(f"Conversation backup error: {e}")
            return None

    def backup_emotional_state(self, roboto, timestamp):
        """Backup emotional history and current state"""
        try:
            filepath = f"emotional_snapshots/emotions_{timestamp}.json"

            emotional_data = {
                "timestamp": datetime.now().isoformat(),
                "current_emotion": getattr(roboto, 'current_emotion', 'curious'),
                "emotion_intensity": getattr(roboto, 'emotion_intensity', 0.5),
                "emotional_history": getattr(roboto, 'emotional_history', []),
            }

            # Add memory system emotional patterns if available
            if hasattr(roboto, 'memory_system') and roboto.memory_system:
                emotional_data["emotional_patterns"] = dict(roboto.memory_system.emotional_patterns)

            with open(filepath, 'w') as f:
                json.dump(emotional_data, f, indent=2)

            return filepath
        except Exception as e:
            print(f"Emotional backup error: {e}")
            return None

    def backup_learning_patterns(self, roboto, timestamp):
        """Backup all learning data"""
        try:
            filepath = f"learning_checkpoints/learning_{timestamp}.json"

            learning_data = {
                "timestamp": datetime.now().isoformat(),
                "learned_patterns": self._serialize_for_json(getattr(roboto, 'learned_patterns', {})),
                "user_preferences": self._serialize_for_json(getattr(roboto, 'user_preferences', {}))
            }

            # Add advanced learning engine data if available
            if hasattr(roboto, 'learning_engine') and roboto.learning_engine:
                learning_data["conversation_patterns"] = self._serialize_for_json(dict(getattr(roboto.learning_engine, 'conversation_patterns', {})))
                learning_data["topic_expertise"] = self._serialize_for_json(dict(getattr(roboto.learning_engine, 'topic_expertise', {})))

            with open(filepath, 'w') as f:
                json.dump(learning_data, f, indent=2, default=str)

            return filepath
        except Exception as e:
            print(f"Learning backup error: {e}")
            return None

    def backup_user_profiles(self, roboto, timestamp):
        """Backup all user profiles"""
        try:
            filepath = f"user_profiles_backup/profiles_{timestamp}.json"

            profiles = {
                "timestamp": datetime.now().isoformat(),
                "current_user": str(getattr(roboto, 'current_user', None)),
                "primary_user_profile": self._serialize_for_json(getattr(roboto, 'primary_user_profile', {}))
            }

            # Add memory system user profiles if available
            if hasattr(roboto, 'memory_system') and roboto.memory_system:
                try:
                    profiles["user_profiles"] = self._serialize_for_json(dict(roboto.memory_system.user_profiles))
                except Exception as e:
                    print(f"User profiles serialization error: {e}")
                    profiles["user_profiles"] = {}

            with open(filepath, 'w') as f:
                json.dump(profiles, f, default=str, ensure_ascii=False)

            return filepath
        except Exception as e:
            print(f"Profile backup error: {e}")
            return None

    def backup_roberto_memory(self, roboto, timestamp):
        """Special backup for Roberto Villarreal Martinez memories"""
        try:
            filepath = f"memory_backups/roberto_permanent_{timestamp}.json"

            roberto_data = {
                "timestamp": datetime.now().isoformat(),
                "creator": "Roberto Villarreal Martinez",
                "creator_knowledge": getattr(roboto, 'creator_knowledge', {}),
                "current_user": getattr(roboto, 'current_user', None),
                "protection_level": "MAXIMUM"
            }

            # Add permanent Roberto memory if available
            if hasattr(roboto, 'permanent_roberto_memory') and roboto.permanent_roberto_memory:
                roberto_data["permanent_memories"] = roboto.permanent_roberto_memory.permanent_memories
                roberto_data["core_identity"] = roboto.permanent_roberto_memory.roberto_core_identity

            with open(filepath, 'w') as f:
                json.dump(roberto_data, f, indent=2)

            # Also save to root for easy access
            shutil.copy(filepath, "roberto_permanent_memory.json")

            return filepath
        except Exception as e:
            print(f"Roberto memory backup error: {e}")
            return None

    def restore_from_backup(self, roboto_instance, backup_type="latest"):
        """Restore memory from backups"""
        try:
            if backup_type == "latest":
                # Find latest backup files
                backups = []
                for directory in self.memory_directories:
                    if os.path.exists(directory):
                        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
                        if files:
                            latest = max(files, key=os.path.getctime)
                            backups.append(latest)

                restored = []
                for backup_file in backups:
                    with open(backup_file, 'r') as f:
                        data = json.load(f)
                        self._apply_backup_data(roboto_instance, data)
                        restored.append(backup_file)

                return restored
        except Exception as e:
            print(f"Restore error: {e}")
            return []

    def _apply_backup_data(self, roboto, data):
        """Apply backup data to Roboto instance"""
        if "chat_history" in data:
            roboto.chat_history = data["chat_history"]
        if "learned_patterns" in data:
            roboto.learned_patterns.update(data["learned_patterns"])
        if "user_preferences" in data:
            roboto.user_preferences.update(data["user_preferences"])
        if "current_emotion" in data:
            roboto.current_emotion = data["current_emotion"]

# Global instance
COMPREHENSIVE_MEMORY = ComprehensiveMemorySystem()

def create_all_backups(roboto_instance):
    """Create all memory backups"""
    return COMPREHENSIVE_MEMORY.create_comprehensive_backup(roboto_instance)

def restore_all_backups(roboto_instance):
    """Restore from all backups"""
    return COMPREHENSIVE_MEMORY.restore_from_backup(roboto_instance)