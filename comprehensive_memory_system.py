
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
        """Create multiple backup files across different systems"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backups_created = []
        
        # 1. Main memory backup
        main_backup = self.backup_main_memory(roboto_instance, timestamp)
        if main_backup:
            backups_created.append(main_backup)
        
        # 2. Conversation archive
        convo_backup = self.backup_conversations(roboto_instance, timestamp)
        if convo_backup:
            backups_created.append(convo_backup)
        
        # 3. Emotional state snapshot
        emotion_backup = self.backup_emotional_state(roboto_instance, timestamp)
        if emotion_backup:
            backups_created.append(emotion_backup)
        
        # 4. Learning patterns checkpoint
        learning_backup = self.backup_learning_patterns(roboto_instance, timestamp)
        if learning_backup:
            backups_created.append(learning_backup)
        
        # 5. User profile backup
        profile_backup = self.backup_user_profiles(roboto_instance, timestamp)
        if profile_backup:
            backups_created.append(profile_backup)
        
        # 6. Roberto-specific permanent memory
        roberto_backup = self.backup_roberto_memory(roboto_instance, timestamp)
        if roberto_backup:
            backups_created.append(roberto_backup)
        
        return backups_created
    
    def backup_main_memory(self, roboto, timestamp):
        """Backup main memory system"""
        try:
            filepath = f"memory_backups/main_memory_{timestamp}.json"
            
            memory_data = {
                "timestamp": datetime.now().isoformat(),
                "chat_history": getattr(roboto, 'chat_history', []),
                "learned_patterns": getattr(roboto, 'learned_patterns', {}),
                "user_preferences": getattr(roboto, 'user_preferences', {}),
                "current_emotion": getattr(roboto, 'current_emotion', 'curious'),
                "current_user": getattr(roboto, 'current_user', None)
            }
            
            with open(filepath, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            return filepath
        except Exception as e:
            print(f"Main memory backup error: {e}")
            return None
    
    def backup_conversations(self, roboto, timestamp):
        """Backup all conversations"""
        try:
            filepath = f"conversation_archives/conversations_{timestamp}.json"
            
            conversations = {
                "timestamp": datetime.now().isoformat(),
                "total_conversations": len(getattr(roboto, 'chat_history', [])),
                "conversations": getattr(roboto, 'chat_history', [])
            }
            
            with open(filepath, 'w') as f:
                json.dump(conversations, f, indent=2)
            
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
                "learned_patterns": getattr(roboto, 'learned_patterns', {}),
                "user_preferences": getattr(roboto, 'user_preferences', {})
            }
            
            # Add advanced learning engine data if available
            if hasattr(roboto, 'learning_engine') and roboto.learning_engine:
                learning_data["conversation_patterns"] = dict(getattr(roboto.learning_engine, 'conversation_patterns', {}))
                learning_data["topic_expertise"] = dict(getattr(roboto.learning_engine, 'topic_expertise', {}))
            
            with open(filepath, 'w') as f:
                json.dump(learning_data, f, indent=2)
            
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
                "current_user": getattr(roboto, 'current_user', None),
                "primary_user_profile": getattr(roboto, 'primary_user_profile', {})
            }
            
            # Add memory system user profiles if available
            if hasattr(roboto, 'memory_system') and roboto.memory_system:
                # Convert any sets to lists for JSON serialization
                user_profiles = dict(roboto.memory_system.user_profiles)
                for key, value in user_profiles.items():
                    if isinstance(value, dict):
                        for k, v in value.items():
                            if isinstance(v, set):
                                value[k] = list(v)
                    elif isinstance(value, set):
                        user_profiles[key] = list(value)
                profiles["user_profiles"] = user_profiles
            
            with open(filepath, 'w') as f:
                json.dump(profiles, f, indent=2)
            
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
