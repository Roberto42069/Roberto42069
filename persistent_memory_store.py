
"""
Persistent Memory Store - Long-term storage with redundancy
Created by Roberto Villarreal Martinez
"""

import json
import os
from datetime import datetime
import sqlite3
from pathlib import Path

class PersistentMemoryStore:
    """Persistent storage with database backend"""
    
    def __init__(self, db_path="persistent_memory.db"):
        self.db_path = db_path
        self.json_store = "persistent_memory_store"
        os.makedirs(self.json_store, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for structured storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                response TEXT,
                emotion TEXT,
                importance REAL
            )
        ''')
        
        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_key TEXT UNIQUE,
                pattern_data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # User data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_key TEXT UNIQUE,
                user_value TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_conversation(self, user_input, response, emotion="neutral", importance=0.5):
        """Store conversation in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (timestamp, user_input, response, emotion, importance)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_input, response, emotion, importance))
        
        conn.commit()
        conn.close()
    
    def store_pattern(self, pattern_key, pattern_data):
        """Store or update learned pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learned_patterns (pattern_key, pattern_data, created_at, updated_at)
            VALUES (?, ?, COALESCE((SELECT created_at FROM learned_patterns WHERE pattern_key = ?), ?), ?)
        ''', (pattern_key, json.dumps(pattern_data), pattern_key, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def export_to_json(self):
        """Export database to JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        conn = sqlite3.connect(self.db_path)
        
        # Export conversations
        conversations = conn.execute('SELECT * FROM conversations').fetchall()
        conv_file = os.path.join(self.json_store, f"conversations_{timestamp}.json")
        with open(conv_file, 'w') as f:
            json.dump([{
                'id': c[0], 'timestamp': c[1], 'user_input': c[2],
                'response': c[3], 'emotion': c[4], 'importance': c[5]
            } for c in conversations], f, indent=2)
        
        # Export patterns
        patterns = conn.execute('SELECT * FROM learned_patterns').fetchall()
        pattern_file = os.path.join(self.json_store, f"patterns_{timestamp}.json")
        with open(pattern_file, 'w') as f:
            json.dump([{
                'id': p[0], 'key': p[1], 'data': p[2], 
                'created': p[3], 'updated': p[4]
            } for p in patterns], f, indent=2)
        
        conn.close()
        return [conv_file, pattern_file]
    
    def get_conversation_count(self):
        """Get total conversation count"""
        conn = sqlite3.connect(self.db_path)
        count = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
        conn.close()
        return count

# Global instance
PERSISTENT_STORE = PersistentMemoryStore()
