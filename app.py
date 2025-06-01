from app1 import Roboto
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response
import os
import io
import base64
import cv2
import threading
import time
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

# Global variables for video capture
camera = None
camera_lock = threading.Lock()
video_active = False

def initialize_camera():
    global camera
    try:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        return camera.isOpened()
    except Exception as e:
        print(f"Camera initialization failed: {e}")
        return False

def generate_frames():
    global camera, video_active
    while video_active:
        with camera_lock:
            if camera is None or not camera.isOpened():
                if not initialize_camera():
                    time.sleep(1)
                    continue
            
            success, frame = camera.read()
            if not success:
                time.sleep(0.1)
                continue
            else:
                # Add timestamp overlay
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Add Roboto status overlay
                cv2.putText(frame, "Roboto Live Video", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)  # ~30 FPS

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
        # Validate request
        data = request.get_json()
        if not data or 'message' not in data:
            app.logger.error("No message provided in chat request")
            return jsonify({"success": False, "response": "No message provided"}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({"success": False, "response": "Empty message"}), 400
            
        user_name = data.get('user_name')
        app.logger.info(f"Chat request from user: {user_name}, message length: {len(message)}")
        
        # Get Roberto instance
        roberto = get_user_roberto()
        if not roberto:
            app.logger.error("Failed to get Roberto instance")
            return jsonify({"success": False, "response": "System initialization error"}), 500
        
        # Set current user if provided
        try:
            if user_name:
                roberto.set_current_user(user_name)
            else:
                roberto.check_user_introduction(message)
        except Exception as e:
            app.logger.warning(f"User setting error: {e}")
        
        # Get memory context with error handling
        relevant_memories = []
        try:
            if roberto.memory_system:
                relevant_memories = roberto.memory_system.retrieve_relevant_memories(
                    message, roberto.current_user, limit=3
                )
        except Exception as e:
            app.logger.warning(f"Memory retrieval error: {e}")
        
        # Detect emotion and update state
        try:
            roberto.detect_emotion(message)
        except Exception as e:
            app.logger.warning(f"Emotion detection error: {e}")
        
        # Generate response with error handling
        response = None
        try:
            response = roberto.generate_response(message)
            if not response:
                response = "I'm experiencing some difficulty right now. Please try again."
        except Exception as e:
            app.logger.error(f"Response generation error: {e}")
            response = "I'm having trouble processing your message right now. Please try again in a moment."
        
        # Store interaction in memory system
        memory_id = None
        try:
            if roberto.memory_system and response:
                memory_id = roberto.memory_system.add_episodic_memory(
                    message, response, roberto.current_emotion, roberto.current_user
                )
        except Exception as e:
            app.logger.warning(f"Memory storage error: {e}")
        
        # Add to chat history
        try:
            chat_entry = {
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "emotion": getattr(roberto, 'current_emotion', 'curious'),
                "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5),
                "memory_id": memory_id,
                "user": getattr(roberto, 'current_user', None)
            }
            roberto.chat_history.append(chat_entry)
            roberto.save_chat_history()
        except Exception as e:
            app.logger.warning(f"Chat history save error: {e}")
        
        # Save user data
        try:
            save_user_data()
        except Exception as e:
            app.logger.warning(f"User data save error: {e}")
        
        # Get updated memory summary
        memory_summary = {}
        try:
            if roberto.memory_system:
                memory_summary = roberto.memory_system.get_memory_summary(roberto.current_user)
        except Exception as e:
            app.logger.warning(f"Memory summary error: {e}")
        
        return jsonify({
            "success": True, 
            "response": response,
            "emotion": getattr(roberto, 'current_emotion', 'curious'),
            "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5),
            "current_user": getattr(roberto, 'current_user', None),
            "memory_context": {
                "relevant_memories": len(relevant_memories),
                "total_user_memories": memory_summary.get('user_specific_memories', 0),
                "memory_id": memory_id
            }
        })
        
    except Exception as e:
        app.logger.error(f"Chat endpoint critical error: {e}")
        return jsonify({
            "success": False, 
            "response": "I'm experiencing technical difficulties. Please refresh the page and try again."
        }), 500

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

@app.route('/api/code-access', methods=['GET'])
def get_code_access():
    """Allow AI to inspect its own code for debugging and improvement"""
    try:
        import os
        import glob
        
        code_files = {}
        
        # Get main application files
        patterns = ['*.py', 'static/js/*.js', 'static/css/*.css', 'templates/*.html']
        for pattern in patterns:
            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code_files[file_path] = f.read()
                    except Exception as e:
                        code_files[file_path] = f"Error reading file: {e}"
        
        return jsonify({
            "success": True,
            "code_files": code_files,
            "message": "Code access granted for self-inspection"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/code-modify', methods=['POST'])
def modify_code():
    """Allow AI to modify its own code"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data or 'content' not in data:
            return jsonify({"success": False, "message": "File path and content required"}), 400
        
        file_path = data['file_path']
        content = data['content']
        
        # Security check - only allow modification of specific files
        allowed_files = ['static/js/app.js', 'static/css/style.css', 'app1.py', 'memory_system.py']
        if file_path not in allowed_files:
            return jsonify({"success": False, "message": "File modification not allowed"}), 403
        
        # Backup original file
        backup_path = f"{file_path}.backup"
        import shutil
        shutil.copy2(file_path, backup_path)
        
        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "success": True,
            "message": f"File {file_path} modified successfully",
            "backup_created": backup_path
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    global video_active
    video_active = True
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_video')
def start_video():
    """Start video capture"""
    global video_active
    video_active = True
    if initialize_camera():
        return jsonify({'success': True, 'message': 'Video started'})
    else:
        return jsonify({'success': False, 'message': 'Failed to initialize camera'})

@app.route('/stop_video')
def stop_video():
    """Stop video capture"""
    global video_active, camera
    video_active = False
    with camera_lock:
        if camera:
            camera.release()
            camera = None
    return jsonify({'success': True, 'message': 'Video stopped'})

@app.route('/speech_to_speech', methods=['POST'])
def speech_to_speech():
    """Process audio input and return audio response using OpenAI's API"""
    try:
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file provided'})
        
        audio_file = request.files['audio']
        
        # Save temporary audio file
        temp_audio_path = f"temp_audio_{datetime.now().timestamp()}.webm"
        audio_file.save(temp_audio_path)
        
        # Transcribe audio using OpenAI Whisper
        with open(temp_audio_path, 'rb') as audio:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        
        # Get text response from Roboto
        roboto = get_user_roberto()
        if roboto:
            response_text = roboto.chat(transcript.text)
        else:
            response_text = "I'm sorry, I couldn't process your request."
        
        # Generate speech from text using OpenAI TTS
        speech_response = openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=response_text,
            response_format="mp3"
        )
        
        # Save speech to temporary file
        temp_speech_path = f"temp_speech_{datetime.now().timestamp()}.mp3"
        speech_response.stream_to_file(temp_speech_path)
        
        # Convert audio to base64 for transmission
        with open(temp_speech_path, 'rb') as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode()
        
        # Clean up temporary files
        os.remove(temp_audio_path)
        os.remove(temp_speech_path)
        
        return jsonify({
            'success': True,
            'transcript': transcript.text,
            'response': response_text,
            'audio': audio_data
        })
        
    except Exception as e:
        print(f"Speech-to-speech error: {e}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Using 0.0.0.0 for accessibility