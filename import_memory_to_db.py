#!/usr/bin/env python3
"""
Simple script to import Roboto's memory from JSON files directly into the database
"""

import json
import os
import hashlib
import psycopg2
from psycopg2.extras import Json
from datetime import datetime

# Database connection from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

def import_memories():
    """Import memories from JSON files to database"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Load current memory from roboto_memory.json
        if os.path.exists('roboto_memory.json'):
            print("Loading roboto_memory.json...")
            with open('roboto_memory.json', 'r') as f:
                memory_data = json.load(f)
            
            # Update user_data with memory system data
            print("Updating user_data with memory system...")
            # Convert complex nested structures to JSON strings
            memory_system = {
                'semantic_memories': memory_data.get('semantic_memories', {}),
                'emotional_patterns': memory_data.get('emotional_patterns', {}),
                'user_profiles': memory_data.get('user_profiles', {}),
                'self_reflections': memory_data.get('self_reflections', []),
                'compressed_learnings': memory_data.get('compressed_learnings', {}),
                'last_saved': memory_data.get('last_saved', datetime.now().isoformat())
            }
            
            cur.execute("""
                UPDATE user_data 
                SET memory_system_data = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = 'roboto_system'
            """, (Json(memory_system),))
            
            # Import episodic memories
            episodic_memories = memory_data.get('episodic_memories', [])
            print(f"Importing {len(episodic_memories)} episodic memories...")
            
            imported = 0
            for memory in episodic_memories[:500]:  # Import first 500 memories to avoid timeout
                # Generate memory ID
                content = f"{memory.get('user_input', '')}{memory.get('roboto_response', '')}"
                memory_id = memory.get('id', '')
                if not memory_id:
                    memory_id = hashlib.md5(content.encode()).hexdigest()[:32]
                
                # Prepare memory content and metadata
                content_data = {
                    'user_input': memory.get('user_input', ''),
                    'roboto_response': memory.get('roboto_response', ''),
                    'key_themes': memory.get('key_themes', [])
                }
                
                meta_data = {
                    'emotion': memory.get('emotion', ''),
                    'user_name': memory.get('user_name', ''),
                    'emotional_intensity': memory.get('emotional_intensity', 0),
                    'timestamp': memory.get('timestamp', '')
                }
                
                # Handle sentiment - it may be a dict, string, or number
                sentiment_value = memory.get('sentiment', 0.0)
                if isinstance(sentiment_value, dict):
                    # If sentiment is a dict, try to extract a numeric value or default to 0
                    sentiment_value = sentiment_value.get('score', sentiment_value.get('compound', 0.0))
                elif isinstance(sentiment_value, str):
                    # Convert string sentiments to numeric values
                    sentiment_map = {
                        'positive': 0.7,
                        'negative': -0.7,
                        'neutral': 0.0,
                        'mixed': 0.0
                    }
                    sentiment_value = sentiment_map.get(sentiment_value.lower(), 0.0)
                
                # Insert or update memory
                cur.execute("""
                    INSERT INTO memory_entries 
                    (user_id, memory_id, content, memory_type, importance_score, 
                     emotional_valence, meta_data, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, memory_id) 
                    DO UPDATE SET 
                        content = EXCLUDED.content,
                        importance_score = EXCLUDED.importance_score,
                        emotional_valence = EXCLUDED.emotional_valence,
                        meta_data = EXCLUDED.meta_data,
                        last_accessed = CURRENT_TIMESTAMP,
                        access_count = memory_entries.access_count + 1
                """, (
                    'roboto_system',
                    memory_id,
                    json.dumps(content_data),
                    'episodic',
                    float(memory.get('importance', 0.5)),
                    float(sentiment_value),
                    Json(meta_data)
                ))
                imported += 1
                
                if imported % 100 == 0:
                    print(f"  Imported {imported} memories...")
            
            print(f"✓ Successfully imported {imported} episodic memories")
        
        # Load backup data
        import glob
        backup_files = glob.glob('roboto_backup_*.json')
        if backup_files:
            latest_backup = sorted(backup_files)[-1]
            print(f"\nLoading backup from {latest_backup}...")
            with open(latest_backup, 'r') as f:
                backup_data = json.load(f)
            
            # Update user_data with backup information
            cur.execute("""
                UPDATE user_data 
                SET current_emotion = %s,
                    current_user_name = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = 'roboto_system'
            """, (
                backup_data.get('current_emotion', 'curious'),
                backup_data.get('current_user_name', 'Roberto')
            ))
            
            # Import some recent chat history as memories
            chat_history = backup_data.get('chat_history', [])
            if chat_history:
                print(f"Importing last 30 chat entries from backup...")
                imported_from_backup = 0
                
                for i, chat in enumerate(chat_history[-30:]):
                    if isinstance(chat, dict):
                        user_msg = chat.get('user', '')
                        assistant_msg = chat.get('assistant', '')
                        
                        if user_msg and assistant_msg:
                            memory_id = hashlib.md5(f"backup_{i}_{user_msg}{assistant_msg}".encode()).hexdigest()[:32]
                            
                            content_data = {
                                'user_input': user_msg,
                                'assistant_response': assistant_msg,
                                'source': 'backup_import'
                            }
                            
                            cur.execute("""
                                INSERT INTO memory_entries 
                                (user_id, memory_id, content, memory_type, importance_score, meta_data)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (user_id, memory_id) DO NOTHING
                            """, (
                                'roboto_system',
                                memory_id,
                                json.dumps(content_data),
                                'episodic',
                                0.3,
                                Json({'source': 'backup', 'backup_file': latest_backup})
                            ))
                            imported_from_backup += 1
                
                print(f"✓ Imported {imported_from_backup} memories from backup")
        
        # Load permanent memories
        if os.path.exists('permanent_roberto_memories.json'):
            print("\nLoading permanent memories...")
            with open('permanent_roberto_memories.json', 'r') as f:
                permanent_data = json.load(f)
            
            imported_permanent = 0
            for key, memory_data in permanent_data.items():
                if isinstance(memory_data, dict):
                    memory_id = hashlib.md5(f"permanent_{key}".encode()).hexdigest()[:32]
                    
                    cur.execute("""
                        INSERT INTO memory_entries 
                        (user_id, memory_id, content, memory_type, importance_score, meta_data)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id, memory_id) DO NOTHING
                    """, (
                        'roboto_system',
                        memory_id,
                        json.dumps(memory_data),
                        'semantic',
                        1.0,  # Maximum importance for permanent memories
                        Json({'source': 'permanent', 'key': key})
                    ))
                    imported_permanent += 1
            
            print(f"✓ Imported {imported_permanent} permanent memories")
        
        # Commit all changes
        conn.commit()
        
        # Show statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN memory_type = 'episodic' THEN 1 END) as episodic,
                COUNT(CASE WHEN memory_type = 'semantic' THEN 1 END) as semantic
            FROM memory_entries 
            WHERE user_id = 'roboto_system'
        """)
        stats = cur.fetchone()
        
        print("\n" + "="*60)
        print("DATABASE UPDATE COMPLETE")
        print("="*60)
        print(f"Total memories in database: {stats[0]}")
        print(f"  - Episodic memories: {stats[1]}")
        print(f"  - Semantic memories: {stats[2]}")
        print("\n✓ Roboto's memory successfully imported to database!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import_memories()