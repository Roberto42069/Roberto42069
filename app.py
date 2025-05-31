from app1 import Roboto
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
from openai import OpenAI
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# Database setup
class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "roboto-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app, model_class=Base)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize authentication
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user
from models import UserData

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Create database tables
with app.app_context():
    db.create_all()

# Global Roboto instance - will be user-specific
roberto = None

def get_user_roberto():
    """Get or create a Roboto instance for the current user"""
    global roberto
    if not current_user.is_authenticated:
        # For anonymous users, use a temporary instance
        if roberto is None:
            roberto = Roboto()
        return roberto
    
    # For authenticated users, load their data
    user_data = UserData.query.filter_by(user_id=current_user.id).first()
    if not user_data:
        # Create new user data
        user_data = UserData()
        user_data.user_id = current_user.id
        db.session.add(user_data)
        db.session.commit()
    
    # Create Roboto instance with user data
    roberto = Roboto()
    if hasattr(roberto, 'load_user_data'):
        roberto.load_user_data(user_data)
    return roberto

def save_user_data():
    """Save current Roboto state to database for authenticated users"""
    if current_user.is_authenticated and roberto:
        user_data = UserData.query.filter_by(user_id=current_user.id).first()
        if user_data and hasattr(roberto, 'save_user_data'):
            roberto.save_user_data(user_data)
            db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('app.html', user=current_user)
    else:
        return render_template('landing.html')

@app.route('/api/intro')
def intro():
    roberto = get_user_roberto()
    message = roberto.introduce()
    save_user_data()
    return jsonify({"message": message})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    roberto = get_user_roberto()
    tasks = roberto.show_tasks()
    save_user_data()
    return jsonify({"success": True, "tasks": tasks})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"success": False, "message": "[ERROR] No task provided!"}), 400

        roberto = get_user_roberto()
        result = roberto.add_task(data['task'])
        save_user_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"[ERROR] {str(e)}"}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    try:
        roberto = get_user_roberto()
        history = roberto.chat_history
        save_user_data()
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "history": [], "message": f"Error: {str(e)}"}), 500

@app.route('/api/analytics/learning-insights', methods=['GET'])
def get_learning_insights():
    try:
        roberto = get_user_roberto()
        insights = {
            "patterns": roberto.learned_patterns,
            "preferences": roberto.user_preferences,
            "conversation_stats": {
                "total_messages": len(roberto.chat_history),
                "total_tasks": len(roberto.tasks)
            }
        }
        save_user_data()
        return jsonify({"success": True, "insights": insights})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/analytics/predictive-insights', methods=['GET'])
def get_predictive_insights():
    try:
        predictions = {
            "task_completion_trend": "Based on your activity, you tend to be most productive in the morning",
            "conversation_patterns": "You often ask about task management and productivity tips",
            "suggested_improvements": ["Consider breaking large tasks into smaller ones", "Set specific time blocks for focused work"]
        }
        return jsonify({"success": True, "predictions": predictions})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/emotional-status', methods=['GET'])
def get_emotional_status():
    try:
        roberto = get_user_roberto()
        emotional_status = {
            "current_emotion": roberto.current_emotion,
            "emotion_intensity": roberto.emotion_intensity,
            "emotional_history": roberto.emotional_history[-5:] if len(roberto.emotional_history) > 5 else roberto.emotional_history
        }
        save_user_data()
        return jsonify({"success": True, "emotional_status": emotional_status})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/data/export', methods=['GET'])
def export_data():
    try:
        roberto = get_user_roberto()
        # Include enhanced memory system data
        export_data = {
            "tasks": roberto.tasks,
            "chat_history": roberto.chat_history,
            "learned_patterns": roberto.learned_patterns,
            "user_preferences": roberto.user_preferences,
            "emotional_history": roberto.emotional_history,
            "current_emotion": roberto.current_emotion,
            "current_user": roberto.current_user,
            "memory_system": {
                "episodic_memories": roberto.memory_system.episodic_memories,
                "semantic_memories": roberto.memory_system.semantic_memories,
                "emotional_patterns": dict(roberto.memory_system.emotional_patterns),
                "user_profiles": roberto.memory_system.user_profiles,
                "self_reflections": roberto.memory_system.self_reflections,
                "compressed_learnings": roberto.memory_system.compressed_learnings
            },
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "2.0"
        }
        return jsonify({"success": True, "data": export_data})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "response": "No message provided"}), 400
        
        message = data['message']
        user_name = data.get('user_name')
        
        roberto = get_user_roberto()
        
        # Set current user if provided
        if user_name:
            roberto.set_current_user(user_name)
        else:
            # Check for user introduction in message
            roberto.check_user_introduction(message)
        
        # Get memory context
        relevant_memories = roberto.memory_system.retrieve_relevant_memories(
            message, roberto.current_user, limit=3
        )
        
        # Detect emotion and update state
        roberto.detect_emotion(message)
        
        # Generate response with memory integration
        response = roberto.generate_response(message)
        
        # Store interaction in memory system
        memory_id = roberto.memory_system.add_episodic_memory(
            message, response, roberto.current_emotion, roberto.current_user
        )
        
        # Add to chat history
        chat_entry = {
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "emotion": roberto.current_emotion,
            "emotion_intensity": roberto.emotion_intensity,
            "memory_id": memory_id,
            "user": roberto.current_user
        }
        roberto.chat_history.append(chat_entry)
        roberto.save_chat_history()
        
        # Save user data
        save_user_data()
        
        # Get updated memory summary
        memory_summary = roberto.memory_system.get_memory_summary(roberto.current_user)
        
        return jsonify({
            "success": True, 
            "response": response,
            "emotion": roberto.current_emotion,
            "emotion_intensity": roberto.emotion_intensity,
            "current_user": roberto.current_user,
            "memory_context": {
                "relevant_memories": len(relevant_memories),
                "total_user_memories": memory_summary.get('user_specific_memories', 0),
                "memory_id": memory_id
            }
        })
    except Exception as e:
        return jsonify({"success": False, "response": f"Error: {str(e)}"}), 500

# Memory Management API Endpoints
@app.route('/api/memory/summary', methods=['GET'])
def get_memory_summary():
    try:
        user_name = request.args.get('user_name')
        summary = roberto.memory_system.get_memory_summary(user_name)
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/user/set', methods=['POST'])
def set_current_user():
    try:
        data = request.get_json()
        user_name = data.get('user_name')
        if not user_name:
            return jsonify({"success": False, "message": "User name required"}), 400
        
        roberto.set_current_user(user_name)
        profile = roberto.memory_system.user_profiles.get(user_name, {})
        return jsonify({"success": True, "current_user": user_name, "profile": profile})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/search', methods=['POST'])
def search_memories():
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_name = data.get('user_name')
        limit = data.get('limit', 10)
        
        memories = roberto.memory_system.retrieve_relevant_memories(query, user_name, limit)
        return jsonify({"success": True, "memories": memories})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/edit', methods=['POST'])
def edit_memory():
    try:
        data = request.get_json()
        memory_id = data.get('memory_id')
        updates = data.get('updates', {})
        
        if not memory_id:
            return jsonify({"success": False, "message": "Memory ID required"}), 400
        
        success = roberto.memory_system.edit_memory(memory_id, updates)
        return jsonify({"success": success, "message": "Memory updated" if success else "Memory not found"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/delete', methods=['POST'])
def delete_memory():
    try:
        data = request.get_json()
        memory_id = data.get('memory_id')
        
        if not memory_id:
            return jsonify({"success": False, "message": "Memory ID required"}), 400
        
        success = roberto.memory_system.remove_memory(memory_id)
        return jsonify({"success": success, "message": "Memory deleted" if success else "Memory not found"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/reflections', methods=['GET'])
def get_reflections():
    try:
        reflections = roberto.memory_system.self_reflections[-10:]  # Last 10 reflections
        return jsonify({"success": True, "reflections": reflections})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/emotional-patterns', methods=['GET'])
def get_emotional_patterns():
    try:
        user_name = request.args.get('user_name')
        if user_name:
            patterns = roberto.memory_system.emotional_patterns.get(user_name, [])
            context = roberto.memory_system.get_emotional_context(user_name)
        else:
            patterns = []
            context = {"current_trend": "neutral", "patterns": []}
        
        return jsonify({
            "success": True, 
            "patterns": patterns[-20:],  # Last 20 patterns
            "context": context
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/memory/add-reflection', methods=['POST'])
def add_reflection():
    try:
        data = request.get_json()
        reflection_text = data.get('reflection')
        trigger_event = data.get('trigger_event')
        
        if not reflection_text:
            return jsonify({"success": False, "message": "Reflection text required"}), 400
        
        reflection_id = roberto.memory_system.add_self_reflection(reflection_text, trigger_event)
        return jsonify({"success": True, "reflection_id": reflection_id})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Using 0.0.0.0 for accessibility