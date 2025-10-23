#!/usr/bin/env python3
"""
Import Roboto's memory data from JSON files into the database
This script updates the database with both current memory and backup memory
"""

import json
import os
from datetime import datetime
from app import app, db
from models import User, UserData, MemoryEntry
import hashlib

def get_or_create_roboto_user():
    """Get or create the Roboto system user"""
    with app.app_context():
        roboto_user = User.query.filter_by(username='roboto_system').first()
        if not roboto_user:
            roboto_user = User(
                username='roboto_system',
                email='roboto@system.local',
                password_hash='system_account'
            )
            db.session.add(roboto_user)
            db.session.commit()
            print("Created Roboto system user")
        else:
            print("Found existing Roboto system user")
        return roboto_user

def import_current_memory(roboto_user):
    """Import current memory from roboto_memory.json"""
    memory_file = 'roboto_memory.json'
    if not os.path.exists(memory_file):
        print(f"Memory file {memory_file} not found")
        return
    
    print(f"\nImporting current memory from {memory_file}...")
    with open(memory_file, 'r') as f:
        memory_data = json.load(f)
    
    # Update or create UserData
    user_data = UserData.query.filter_by(user_id=roboto_user.id).first()
    if not user_data:
        user_data = UserData(user_id=roboto_user.id)
        db.session.add(user_data)
    
    # Store the entire memory system data
    user_data.memory_system_data = {
        'semantic_memories': memory_data.get('semantic_memories', {}),
        'emotional_patterns': memory_data.get('emotional_patterns', {}),
        'user_profiles': memory_data.get('user_profiles', {}),
        'self_reflections': memory_data.get('self_reflections', []),
        'compressed_learnings': memory_data.get('compressed_learnings', {}),
        'last_saved': memory_data.get('last_saved', datetime.now().isoformat())
    }
    
    # Import episodic memories as individual MemoryEntry records
    episodic_memories = memory_data.get('episodic_memories', [])
    print(f"Processing {len(episodic_memories)} episodic memories...")
    
    imported_count = 0
    updated_count = 0
    
    for memory in episodic_memories:
        # Generate or use existing memory ID
        memory_id = memory.get('id', '')
        if not memory_id:
            # Generate ID from content
            content = f"{memory.get('user_input', '')}{memory.get('roboto_response', '')}"
            memory_id = hashlib.md5(content.encode()).hexdigest()
        
        # Check if memory entry exists
        existing_memory = MemoryEntry.query.filter_by(
            user_id=roboto_user.id,
            memory_id=memory_id
        ).first()
        
        if existing_memory:
            # Update existing memory
            existing_memory.content = json.dumps({
                'user_input': memory.get('user_input', ''),
                'roboto_response': memory.get('roboto_response', ''),
                'key_themes': memory.get('key_themes', [])
            })
            existing_memory.importance_score = memory.get('importance', 0.5)
            existing_memory.emotional_valence = memory.get('sentiment', 0.0)
            existing_memory.metadata = {
                'emotion': memory.get('emotion', ''),
                'user_name': memory.get('user_name', ''),
                'emotional_intensity': memory.get('emotional_intensity', 0),
                'timestamp': memory.get('timestamp', '')
            }
            existing_memory.last_accessed = datetime.utcnow()
            updated_count += 1
        else:
            # Create new memory entry
            new_memory = MemoryEntry(
                user_id=roboto_user.id,
                memory_id=memory_id,
                content=json.dumps({
                    'user_input': memory.get('user_input', ''),
                    'roboto_response': memory.get('roboto_response', ''),
                    'key_themes': memory.get('key_themes', [])
                }),
                memory_type='episodic',
                importance_score=memory.get('importance', 0.5),
                emotional_valence=memory.get('sentiment', 0.0),
                metadata={
                    'emotion': memory.get('emotion', ''),
                    'user_name': memory.get('user_name', ''),
                    'emotional_intensity': memory.get('emotional_intensity', 0),
                    'timestamp': memory.get('timestamp', '')
                }
            )
            db.session.add(new_memory)
            imported_count += 1
    
    db.session.commit()
    print(f"✓ Imported {imported_count} new memories, updated {updated_count} existing memories")
    print(f"✓ Updated user memory system data")

def import_backup_memory(roboto_user):
    """Import backup memory from the latest backup file"""
    import glob
    
    # Find the latest backup file
    backup_files = glob.glob('roboto_backup_*.json')
    if not backup_files:
        print("No backup files found")
        return
    
    latest_backup = sorted(backup_files)[-1]
    print(f"\nImporting backup memory from {latest_backup}...")
    
    with open(latest_backup, 'r') as f:
        backup_data = json.load(f)
    
    # Get or update UserData with backup information
    user_data = UserData.query.filter_by(user_id=roboto_user.id).first()
    if not user_data:
        user_data = UserData(user_id=roboto_user.id)
        db.session.add(user_data)
    
    # Merge backup data with existing memory system data
    if not user_data.memory_system_data:
        user_data.memory_system_data = {}
    
    # Add backup-specific data
    user_data.memory_system_data['backup_data'] = {
        'chat_history_count': len(backup_data.get('chat_history', [])),
        'learned_patterns': backup_data.get('learned_patterns', {}),
        'user_preferences': backup_data.get('user_preferences', {}),
        'emotional_history': backup_data.get('emotional_history', [])[-100:],  # Keep last 100
        'learning_data': backup_data.get('learning_data', {}),
        'optimization_data': backup_data.get('optimization_data', {}),
        'last_backup': backup_data.get('last_backup', latest_backup)
    }
    
    # Update current state from backup
    user_data.current_emotion = backup_data.get('current_emotion', 'curious')
    user_data.current_user_name = backup_data.get('current_user_name', None)
    
    # Process chat history into memories if needed
    chat_history = backup_data.get('chat_history', [])
    if chat_history:
        print(f"Processing {len(chat_history)} chat history entries...")
        
        imported_from_backup = 0
        for i, chat in enumerate(chat_history[-50:]):  # Process last 50 chat entries
            if isinstance(chat, dict):
                user_msg = chat.get('user', '')
                assistant_msg = chat.get('assistant', '')
                
                if user_msg and assistant_msg:
                    # Generate memory ID from chat content
                    memory_id = hashlib.md5(f"backup_{i}_{user_msg}{assistant_msg}".encode()).hexdigest()
                    
                    # Check if this backup memory exists
                    existing = MemoryEntry.query.filter_by(
                        user_id=roboto_user.id,
                        memory_id=memory_id
                    ).first()
                    
                    if not existing:
                        new_memory = MemoryEntry(
                            user_id=roboto_user.id,
                            memory_id=memory_id,
                            content=json.dumps({
                                'user_input': user_msg,
                                'assistant_response': assistant_msg,
                                'source': 'backup_import'
                            }),
                            memory_type='episodic',
                            importance_score=0.3,  # Lower importance for backup entries
                            metadata={
                                'source': 'backup',
                                'backup_file': latest_backup,
                                'import_date': datetime.now().isoformat()
                            }
                        )
                        db.session.add(new_memory)
                        imported_from_backup += 1
        
        print(f"✓ Imported {imported_from_backup} memories from backup chat history")
    
    db.session.commit()
    print(f"✓ Updated user data with backup information from {latest_backup}")

def import_permanent_memories(roboto_user):
    """Import permanent Roberto memories if they exist"""
    permanent_file = 'permanent_roberto_memories.json'
    if not os.path.exists(permanent_file):
        print(f"Permanent memories file {permanent_file} not found")
        return
    
    print(f"\nImporting permanent memories from {permanent_file}...")
    with open(permanent_file, 'r') as f:
        permanent_data = json.load(f)
    
    imported_permanent = 0
    for key, memory_data in permanent_data.items():
        if isinstance(memory_data, dict):
            # Generate memory ID
            memory_id = hashlib.md5(f"permanent_{key}".encode()).hexdigest()
            
            # Check if exists
            existing = MemoryEntry.query.filter_by(
                user_id=roboto_user.id,
                memory_id=memory_id
            ).first()
            
            if not existing:
                new_memory = MemoryEntry(
                    user_id=roboto_user.id,
                    memory_id=memory_id,
                    content=json.dumps(memory_data),
                    memory_type='semantic',  # Permanent memories are semantic
                    importance_score=1.0,  # Maximum importance
                    metadata={
                        'source': 'permanent',
                        'key': key,
                        'import_date': datetime.now().isoformat()
                    }
                )
                db.session.add(new_memory)
                imported_permanent += 1
    
    if imported_permanent > 0:
        db.session.commit()
        print(f"✓ Imported {imported_permanent} permanent memories")

def main():
    """Main import function"""
    print("="*60)
    print("ROBOTO MEMORY DATABASE IMPORT")
    print("="*60)
    
    with app.app_context():
        # Get or create Roboto user
        roboto_user = get_or_create_roboto_user()
        
        # Import current memory
        import_current_memory(roboto_user)
        
        # Import backup memory
        import_backup_memory(roboto_user)
        
        # Import permanent memories
        import_permanent_memories(roboto_user)
        
        # Show statistics
        print("\n" + "="*60)
        print("IMPORT COMPLETE - DATABASE STATISTICS")
        print("="*60)
        
        total_memories = MemoryEntry.query.filter_by(user_id=roboto_user.id).count()
        episodic_count = MemoryEntry.query.filter_by(
            user_id=roboto_user.id,
            memory_type='episodic'
        ).count()
        semantic_count = MemoryEntry.query.filter_by(
            user_id=roboto_user.id,
            memory_type='semantic'
        ).count()
        
        print(f"Total memory entries in database: {total_memories}")
        print(f"  - Episodic memories: {episodic_count}")
        print(f"  - Semantic memories: {semantic_count}")
        
        user_data = UserData.query.filter_by(user_id=roboto_user.id).first()
        if user_data and user_data.memory_system_data:
            print(f"\nMemory system data keys: {list(user_data.memory_system_data.keys())}")
            if 'backup_data' in user_data.memory_system_data:
                backup_info = user_data.memory_system_data['backup_data']
                print(f"Backup data includes:")
                print(f"  - Chat history count: {backup_info.get('chat_history_count', 0)}")
                print(f"  - Last backup: {backup_info.get('last_backup', 'Unknown')}")
        
        print("\n✓ Database successfully updated with Roboto's memory!")

if __name__ == "__main__":
    main()