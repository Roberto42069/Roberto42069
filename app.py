from app1 import Roboto
from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "roboto-secret-key")

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

roberto = Roboto()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/intro')
def intro():
    return jsonify({"message": roberto.introduce()})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({"success": True, "tasks": roberto.show_tasks()})  # Adjusted line

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"success": False, "message": "[ERROR] No task provided!"}), 400

        result = roberto.add_task(data['task'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"[ERROR] {str(e)}"}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    try:
        history = roberto.chat_history
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "history": [], "message": f"Error: {str(e)}"}), 500

@app.route('/api/analytics/learning-insights', methods=['GET'])
def get_learning_insights():
    try:
        insights = {
            "patterns": roberto.learned_patterns,
            "preferences": roberto.user_preferences,
            "conversation_stats": {
                "total_messages": len(roberto.chat_history),
                "total_tasks": len(roberto.tasks)
            }
        }
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
        emotional_status = {
            "current_emotion": roberto.current_emotion,
            "emotion_intensity": roberto.emotion_intensity,
            "emotional_history": roberto.emotional_history[-5:] if len(roberto.emotional_history) > 5 else roberto.emotional_history
        }
        return jsonify({"success": True, "emotional_status": emotional_status})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/data/export', methods=['GET'])
def export_data():
    try:
        export_data = {
            "tasks": roberto.tasks,
            "chat_history": roberto.chat_history,
            "learned_patterns": roberto.learned_patterns,
            "user_preferences": roberto.user_preferences,
            "emotional_history": roberto.emotional_history,
            "current_emotion": roberto.current_emotion,
            "export_timestamp": "2025-05-30T13:00:00Z"
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
            "timestamp": roberto.get_timestamp(),
            "emotion": roberto.current_emotion,
            "emotion_intensity": roberto.emotion_intensity,
            "memory_id": memory_id,
            "user": roberto.current_user
        }
        roberto.chat_history.append(chat_entry)
        roberto.save_chat_history()
        
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Using 0.0.0.0 for accessibility