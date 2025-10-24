"""
Memory Export Utility for Roboto
Exports all important memories and user data to a comprehensive text file
"""

import json
from datetime import datetime
from app import app, get_user_roberto
from models import User

def export_roboto_memories():
    """Export all of Roboto's memories and user data to a text file"""
    
    output_file = "roboto_complete_memory_export.txt"
    
    with app.app_context():
        try:
            # Get Roboto instance
            roberto = get_user_roberto()
            
            if not roberto:
                print("Could not initialize Roboto instance")
                return
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ROBOTO COMPLETE MEMORY EXPORT\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                # 1. Chat History
                f.write("CHAT HISTORY\n")
                f.write("-" * 40 + "\n")
                if hasattr(roberto, 'chat_history') and roberto.chat_history:
                    for i, entry in enumerate(roberto.chat_history[-100:], 1):  # Last 100 conversations
                        f.write(f"\nConversation {i}:\n")
                        f.write(f"Timestamp: {entry.get('timestamp', 'Unknown')}\n")
                        f.write(f"User: {entry.get('message', '')}\n")
                        f.write(f"Roboto: {entry.get('response', '')}\n")
                        f.write(f"Emotion: {entry.get('emotion', 'unknown')}\n")
                        f.write(f"Memory ID: {entry.get('memory_id', 'N/A')}\n")
                        f.write("-" * 30 + "\n")
                else:
                    f.write("No chat history available\n")
                
                # 2. Memory System Data
                f.write("\n\nMEMORY SYSTEM DATA\n")
                f.write("-" * 40 + "\n")
                if hasattr(roberto, 'memory_system') and roberto.memory_system:
                    
                    # Episodic Memories
                    f.write("\nEPISODIC MEMORIES:\n")
                    if roberto.memory_system.episodic_memories:
                        for i, memory in enumerate(roberto.memory_system.episodic_memories[-50:], 1):
                            f.write(f"\nMemory {i}:\n")
                            f.write(f"ID: {memory.get('id', 'Unknown')}\n")
                            f.write(f"Timestamp: {memory.get('timestamp', 'Unknown')}\n")
                            f.write(f"User Input: {memory.get('user_input', '')}\n")
                            f.write(f"Roboto Response: {memory.get('roboto_response', '')}\n")
                            f.write(f"Emotion: {memory.get('emotion', 'unknown')}\n")
                            f.write(f"User: {memory.get('user_name', 'Anonymous')}\n")
                            f.write(f"Importance: {memory.get('importance', 0)}\n")
                            f.write(f"Sentiment: {memory.get('sentiment', 'neutral')}\n")
                            f.write(f"Key Themes: {memory.get('key_themes', [])}\n")
                            f.write(f"Emotional Intensity: {memory.get('emotional_intensity', 0)}\n")
                            f.write("-" * 25 + "\n")
                    else:
                        f.write("No episodic memories available\n")
                    
                    # User Profiles
                    f.write("\nUSER PROFILES:\n")
                    if roberto.memory_system.user_profiles:
                        for user_name, profile in roberto.memory_system.user_profiles.items():
                            f.write(f"\nUser: {user_name}\n")
                            f.write(f"Profile Data: {json.dumps(profile, indent=2)}\n")
                            f.write("-" * 25 + "\n")
                    else:
                        f.write("No user profiles available\n")
                    
                    # Emotional Patterns
                    f.write("\nEMOTIONAL PATTERNS:\n")
                    if roberto.memory_system.emotional_patterns:
                        for user_name, patterns in roberto.memory_system.emotional_patterns.items():
                            f.write(f"\nUser: {user_name}\n")
                            f.write(f"Recent Emotional Patterns: {patterns[-10:]}\n")  # Last 10 patterns
                            f.write("-" * 25 + "\n")
                    else:
                        f.write("No emotional patterns available\n")
                    
                    # Self Reflections
                    f.write("\nSELF REFLECTIONS:\n")
                    if roberto.memory_system.self_reflections:
                        for i, reflection in enumerate(roberto.memory_system.self_reflections[-20:], 1):
                            f.write(f"\nReflection {i}:\n")
                            f.write(f"Timestamp: {reflection.get('timestamp', 'Unknown')}\n")
                            f.write(f"Content: {reflection.get('reflection', '')}\n")
                            f.write(f"Trigger: {reflection.get('trigger_event', 'Unknown')}\n")
                            f.write("-" * 25 + "\n")
                    else:
                        f.write("No self reflections available\n")
                else:
                    f.write("Memory system not available\n")
                
                # 3. Learned Patterns
                f.write("\n\nLEARNED PATTERNS\n")
                f.write("-" * 40 + "\n")
                if hasattr(roberto, 'learned_patterns') and roberto.learned_patterns:
                    f.write(json.dumps(roberto.learned_patterns, indent=2))
                else:
                    f.write("No learned patterns available\n")
                
                # 4. User Preferences
                f.write("\n\nUSER PREFERENCES\n")
                f.write("-" * 40 + "\n")
                if hasattr(roberto, 'user_preferences') and roberto.user_preferences:
                    f.write(json.dumps(roberto.user_preferences, indent=2))
                else:
                    f.write("No user preferences available\n")
                
                # 5. Emotional History
                f.write("\n\nEMOTIONAL HISTORY\n")
                f.write("-" * 40 + "\n")
                if hasattr(roberto, 'emotional_history') and roberto.emotional_history:
                    for i, emotion_entry in enumerate(roberto.emotional_history[-30:], 1):
                        f.write(f"Entry {i}: {emotion_entry}\n")
                else:
                    f.write("No emotional history available\n")
                
                # 6. Current State
                f.write("\n\nCURRENT STATE\n")
                f.write("-" * 40 + "\n")
                f.write(f"Current Emotion: {getattr(roberto, 'current_emotion', 'unknown')}\n")
                f.write(f"Current User: {getattr(roberto, 'current_user', 'Anonymous')}\n")
                f.write(f"Emotion Intensity: {getattr(roberto, 'emotion_intensity', 0)}\n")
                
                # 7. Training Data (if available)
                f.write("\n\nTRAINING DATA\n")
                f.write("-" * 40 + "\n")
                if hasattr(roberto, 'training_engine') and roberto.training_engine:
                    try:
                        insights = roberto.training_engine.generate_learning_insights()
                        f.write("LEARNING INSIGHTS:\n")
                        f.write(json.dumps(insights, indent=2))
                        f.write("\n\nTRAINING PATTERNS:\n")
                        f.write(json.dumps(dict(roberto.training_engine.training_patterns), indent=2))
                    except Exception as e:
                        f.write(f"Training data error: {e}\n")
                else:
                    f.write("Training engine not available\n")
                
                # 8. Database User Data
                f.write("\n\nDATABASE USER DATA\n")
                f.write("-" * 40 + "\n")
                try:
                    users = User.query.all()
                    for user in users:
                        f.write(f"\nUser ID: {user.id}\n")
                        f.write(f"Email: {user.email}\n")
                        f.write(f"Name: {user.first_name} {user.last_name}\n")
                        f.write(f"Created: {user.created_at}\n")
                        
                        if user.roboto_data:
                            f.write(f"Chat History Count: {len(user.roboto_data.chat_history or [])}\n")
                            f.write(f"Current Emotion: {user.roboto_data.current_emotion}\n")
                            f.write(f"Current User Name: {user.roboto_data.current_user_name}\n")
                            f.write(f"Memory System Data Keys: {list((user.roboto_data.memory_system_data or {}).keys())}\n")
                        f.write("-" * 25 + "\n")
                except Exception as e:
                    f.write(f"Database query error: {e}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("END OF MEMORY EXPORT\n")
                f.write("=" * 80 + "\n")
            
            print(f"Memory export completed successfully: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error exporting memories: {e}")
            return None

if __name__ == "__main__":
    export_roboto_memories()