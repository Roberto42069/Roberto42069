from app1 import Roboto
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response, make_response
import os
import io
import base64
import json
from openai import OpenAI
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user, login_required
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from security_middleware import SecurityManager, require_auth, validate_password_strength, encrypt_sensitive_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'replit_auth.login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(user_id)

# Register authentication blueprint
from replit_auth import make_replit_blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

with app.app_context():
    import models
    db.create_all()

# Global Roberto instance
roberto = None

def make_session_permanent():
    """Make session permanent"""
    session.permanent = True

def get_user_roberto():
    """Get or create a Roboto instance for the current user"""
    global roberto
    
    if roberto is None:
        app.logger.info("Creating new Roberto instance")
        roberto = Roboto()
        
        # Load user data if authenticated
        try:
            from flask_login import current_user
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                try:
                    if hasattr(current_user, 'roboto_data') and current_user.roboto_data:
                        user_data = {
                            'chat_history': getattr(current_user.roboto_data, 'chat_history', []) or [],
                            'learned_patterns': getattr(current_user.roboto_data, 'learned_patterns', {}) or {},
                            'user_preferences': getattr(current_user.roboto_data, 'user_preferences', {}) or {},
                            'emotional_history': getattr(current_user.roboto_data, 'emotional_history', []) or [],
                            'memory_system_data': getattr(current_user.roboto_data, 'memory_system_data', {}) or {},
                            'current_emotion': getattr(current_user.roboto_data, 'current_emotion', 'curious') or 'curious',
                            'current_user_name': getattr(current_user.roboto_data, 'current_user_name', None)
                        }
                        roberto.load_user_data(user_data)
                        app.logger.info(f"Successfully loaded user data for user: {current_user.id}")
                except Exception as e:
                    app.logger.warning(f"Error loading specific user data: {e}")
                    app.logger.info(f"Loaded user data for authenticated user: {current_user.id}")
        except Exception as e:
            app.logger.warning(f"Could not load user data: {e}")
    
    return roberto

def save_user_data():
    """Save current Roboto state with enhanced learning data (database-independent)"""
    try:
        # Save to local files when database is unavailable
        if roberto:
            # Prepare comprehensive user data
            user_data = {
                'chat_history': getattr(roberto, 'chat_history', []),
                'learned_patterns': getattr(roberto, 'learned_patterns', {}),
                'user_preferences': getattr(roberto, 'user_preferences', {}),
                'emotional_history': getattr(roberto, 'emotional_history', []),
                'memory_system_data': getattr(roberto.memory_system, 'memory_data', {}) if hasattr(roberto, 'memory_system') and roberto.memory_system else {},
                'current_emotion': getattr(roberto, 'current_emotion', 'curious'),
                'current_user_name': getattr(roberto, 'current_user', None),
                'learning_data': {},
                'optimization_data': {}
            }
            
            # Collect learning engine data
            if hasattr(roberto, 'learning_engine') and roberto.learning_engine:
                try:
                    roberto.learning_engine.save_learning_data()
                    user_data['learning_data'] = {
                        'performance_metrics': getattr(roberto.learning_engine, 'learning_metrics', {}),
                        'topic_expertise': dict(getattr(roberto.learning_engine, 'topic_expertise', {})),
                        'conversation_patterns': dict(getattr(roberto.learning_engine, 'conversation_patterns', {}))
                    }
                except Exception as e:
                    app.logger.warning(f"Learning engine save error: {e}")
            
            # Collect optimization data
            if hasattr(roberto, 'learning_optimizer') and roberto.learning_optimizer:
                try:
                    roberto.learning_optimizer.save_optimization_data()
                    insights = roberto.learning_optimizer.get_optimization_insights()
                    user_data['optimization_data'] = insights
                except Exception as e:
                    app.logger.warning(f"Learning optimizer save error: {e}")
            
            # Save to Roboto's internal system
            roberto.save_user_data(user_data)
            
            # Try database save, fallback to file if needed
            try:
                from flask_login import current_user
                if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                    if not hasattr(current_user, 'roboto_data') or current_user.roboto_data is None:
                        from models import UserData
                        current_user.roboto_data = UserData()
                        current_user.roboto_data.user_id = current_user.id
                        db.session.add(current_user.roboto_data)
                    
                    # Update database fields
                    current_user.roboto_data.chat_history = user_data.get('chat_history', [])
                    current_user.roboto_data.learned_patterns = user_data.get('learned_patterns', {})
                    current_user.roboto_data.user_preferences = user_data.get('user_preferences', {})
                    current_user.roboto_data.emotional_history = user_data.get('emotional_history', [])
                    current_user.roboto_data.memory_system_data = user_data.get('memory_system_data', {})
                    current_user.roboto_data.current_emotion = user_data.get('current_emotion', 'curious')
                    current_user.roboto_data.current_user_name = user_data.get('current_user_name', None)
                    
                    db.session.commit()
                    app.logger.info("User data saved successfully to database")
                else:
                    # Save to file backup when not authenticated
                    _save_to_file_backup(user_data)
                    
            except Exception as db_error:
                app.logger.warning(f"Database save failed: {db_error}, using file backup")
                _save_to_file_backup(user_data)
                
    except Exception as e:
        app.logger.error(f"Critical error saving user data: {e}")

def _save_to_file_backup(user_data):
    """Save user data to file backup when database is unavailable"""
    try:
        import json
        from datetime import datetime
        
        backup_file = f"roboto_backup_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Load existing backup if it exists
        existing_data = {}
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as f:
                    existing_data = json.load(f)
            except:
                pass
        
        # Update with current data
        existing_data.update(user_data)
        existing_data['last_backup'] = datetime.now().isoformat()
        
        # Save updated backup
        with open(backup_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        app.logger.info(f"User data backed up to {backup_file}")
        
    except Exception as e:
        app.logger.error(f"File backup failed: {e}")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return render_template('landing.html')

@app.route('/app')
@login_required
def app_main():
    make_session_permanent()
    return render_template('index.html')

@app.route('/intro')
@login_required
def intro():
    roberto = get_user_roberto()
    if roberto:
        intro_message = roberto.introduce()
        return jsonify({"success": True, "message": intro_message})
    return jsonify({"success": False, "message": "System not ready"})



@app.route('/api/history', methods=['GET'])
@login_required
def get_chat_history():
    try:
        user_data = current_user.roboto_data
        if user_data and user_data.chat_history:
            return jsonify({"success": True, "history": user_data.chat_history})
        else:
            return jsonify({"success": True, "history": []})
    except Exception as e:
        app.logger.error(f"Error getting chat history: {e}")
        return jsonify({"success": False, "history": []})



@app.route('/api/emotional-status', methods=['GET'])
@login_required
def get_emotional_status():
    try:
        roberto = get_user_roberto()
        if not roberto:
            return jsonify({"success": False, "emotion": "curious", "intensity": 0.5}), 500
        
        emotion = getattr(roberto, 'current_emotion', 'curious')
        intensity = getattr(roberto, 'emotion_intensity', 0.5)
        
        return jsonify({
            "success": True,
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "emotion": "curious", "intensity": 0.5}), 500

@app.route('/api/export', methods=['GET'])
@login_required
def export_data():
    try:
        roberto = get_user_roberto()
        if not roberto:
            return jsonify({"success": False, "message": "No data to export"}), 500
        
        export_data = {
            "chat_history": getattr(roberto, 'chat_history', []),
            "emotional_history": getattr(roberto, 'emotional_history', []),
            "learned_patterns": getattr(roberto, 'learned_patterns', {}),
            "user_preferences": getattr(roberto, 'user_preferences', {}),
            "current_emotion": getattr(roberto, 'current_emotion', 'curious'),
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "2.0"
        }
        return jsonify({"success": True, "data": export_data})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/cookies/set', methods=['POST'])
@login_required
def set_cookies():
    """Set cookies for user preferences and data"""
    try:
        data = request.get_json()
        response = make_response(jsonify({"success": True, "message": "Cookies set"}))
        
        # Set various cookies with user data
        for key, value in data.items():
            response.set_cookie(
                key, 
                str(value), 
                max_age=30*24*60*60,  # 30 days
                secure=True,
                httponly=False,  # Allow JavaScript access
                samesite='Lax'
            )
        
        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cookies/get', methods=['GET'])
@login_required
def get_cookies():
    """Get all available cookies"""
    try:
        cookies = dict(request.cookies)
        return jsonify({"success": True, "cookies": cookies})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cookies/user-data', methods=['POST'])
@login_required
def set_user_data_cookies():
    """Set cookies with user conversation and preference data"""
    try:
        user_data = current_user.roboto_data
        if user_data:
            response = make_response(jsonify({"success": True, "message": "User data cookies set"}))
            
            # Set cookies with user information
            response.set_cookie('user_conversations_count', str(len(user_data.chat_history or [])), max_age=30*24*60*60)
            response.set_cookie('user_emotion', user_data.current_emotion or 'curious', max_age=30*24*60*60)
            response.set_cookie('user_name', user_data.current_user_name or 'Unknown', max_age=30*24*60*60)
            response.set_cookie('user_preferences', str(user_data.user_preferences or {}), max_age=30*24*60*60)
            
            return response
        else:
            return jsonify({"success": False, "message": "No user data found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/keep-alive', methods=['POST'])
@login_required
def keep_alive():
    """Keep session alive - called by service worker"""
    try:
        return jsonify({"success": True, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/import', methods=['POST'])
@login_required
def import_data():
    try:
        import_data_str = request.form.get('import_data')
        if not import_data_str:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        import_data = json.loads(import_data_str)
        
        # Get current user's Roboto instance
        roberto = get_user_roberto()
        if not roberto:
            return jsonify({"success": False, "message": "System not ready"}), 500
        
        # Import data into Roboto instance
        if 'chat_history' in import_data:
            roberto.chat_history.extend(import_data['chat_history'])
        
        if 'emotional_history' in import_data:
            roberto.emotional_history.extend(import_data['emotional_history'])
        
        if 'learned_patterns' in import_data:
            roberto.learned_patterns.update(import_data['learned_patterns'])
        
        if 'user_preferences' in import_data:
            roberto.user_preferences.update(import_data['user_preferences'])
        
        if 'current_emotion' in import_data:
            roberto.current_emotion = import_data['current_emotion']
        
        # Save imported data to database
        save_user_data()
        
        return jsonify({
            "success": True, 
            "message": f"Successfully imported {len(import_data.get('chat_history', []))} conversations and related data"
        })
        
    except json.JSONDecodeError:
        return jsonify({"success": False, "message": "Invalid JSON format"}), 400
    except Exception as e:
        app.logger.error(f"Import error: {e}")
        return jsonify({"success": False, "message": f"Import failed: {str(e)}"}), 500

def handle_file_upload():
    """Handle file uploads including images"""
    try:
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"success": False, "response": "No file selected"}), 400
        
        # Check if it's an image file
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if file.filename and '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({"success": False, "response": f"Invalid file format. Supported formats: {', '.join(allowed_extensions)}"}), 400
        
        # Read and encode the image
        file_content = file.read()
        base64_image = base64.b64encode(file_content).decode('utf-8')
        
        # Get OpenAI client
        openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Analyze the image using OpenAI's vision model
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image in detail. Describe what you see, the context, any notable elements, emotions conveyed, and provide insights about what might be happening in the image. Be thorough and engaging in your analysis."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{file_extension};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        analysis = response.choices[0].message.content
        
        # Get Roberto instance and process the interaction
        roberto = get_user_roberto()
        if roberto:
            # Create a message indicating an image was shared
            image_message = f"📷 Shared an image: {file.filename}"
            
            # Add to chat history
            chat_entry = {
                "message": image_message,
                "response": analysis,
                "timestamp": datetime.now().isoformat(),
                "emotion": getattr(roberto, 'current_emotion', 'curious'),
                "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5),
                "user": getattr(roberto, 'current_user', None),
                "image_analysis": True
            }
            roberto.chat_history.append(chat_entry)
            roberto.save_chat_history()
            
            # Store in memory system
            if hasattr(roberto, 'memory_system') and roberto.memory_system:
                roberto.memory_system.add_episodic_memory(
                    image_message, analysis, roberto.current_emotion, roberto.current_user
                )
            
            save_user_data()
        
        return jsonify({
            "success": True,
            "response": analysis,
            "emotion": getattr(roberto, 'current_emotion', 'curious'),
            "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5)
        })
        
    except Exception as e:
        app.logger.error(f"File upload error: {e}")
        return jsonify({"success": False, "response": f"Error processing image: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        # Check if this is a file upload or regular chat
        if 'file' in request.files:
            return handle_file_upload()
        
        # Validate request
        data = request.get_json()
        if not data or 'message' not in data:
            app.logger.error("No message provided in chat request")
            return jsonify({"success": False, "response": "No message provided"}), 400
        
        message = data['message'].strip()
        image_data = data.get('image')  # Check for base64 image data
        
        if not message and not image_data:
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
                if hasattr(roberto, 'set_current_user'):
                    roberto.set_current_user(user_name)
                if hasattr(roberto, 'memory_system') and roberto.memory_system:
                    # Set user for memory system if it supports it
                    if hasattr(roberto.memory_system, 'current_user'):
                        roberto.memory_system.current_user = user_name
            else:
                roberto.check_user_introduction(message)
        except Exception as e:
            app.logger.warning(f"User setting error: {e}")
        
        # Get memory context with error handling
        relevant_memories = []
        try:
            if hasattr(roberto, 'memory_system') and roberto.memory_system:
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
            if hasattr(roberto, 'memory_system') and roberto.memory_system and response:
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
            if hasattr(roberto, 'memory_system') and roberto.memory_system:
                memory_summary = roberto.memory_system.get_memory_summary(roberto.current_user)
        except Exception as e:
            app.logger.warning(f"Memory summary error: {e}")
        
        return jsonify({
            "success": True,
            "response": response,
            "emotion": getattr(roberto, 'current_emotion', 'curious'),
            "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5),
            "memory_summary": memory_summary,
            "relevant_memories": relevant_memories[:2]  # Limit to 2 most relevant
        })
        
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return jsonify({"success": False, "response": "An unexpected error occurred. Please try again."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)