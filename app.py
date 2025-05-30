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
        response = roberto.chat(message)
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "response": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Using 0.0.0.0 for accessibility