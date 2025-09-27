import os
import logging
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import traceback
from simple_voice_cloning import SimpleVoiceCloning

# Set up logging
logging.basicConfig(level=logging.INFO)

def process_voice_message(audio_file_path, roberto_instance):
    """Process voice message with emotion detection and generate contextual response"""
    try:
        if hasattr(roberto_instance, 'advanced_voice_processor') and roberto_instance.advanced_voice_processor:
            # Transcribe and analyze the audio
            transcription = roberto_instance.advanced_voice_processor.transcribe_audio(audio_file_path)
            emotions = roberto_instance.advanced_voice_processor.detect_emotions(audio_file_path)
            
            # Get the dominant emotion
            dominant_emotion = emotions[0] if emotions else {"label": "neutral", "score": 0.5}
            
            app.logger.info(f"Voice transcription: {transcription[:50]}...")
            app.logger.info(f"Detected emotion: {dominant_emotion}")
            
            # Create emotionally-aware response
            if transcription and "error" not in transcription.lower():
                # Generate response that acknowledges the emotion and transcription
                emotional_context = f"[Voice message detected with {dominant_emotion['label']} emotion at {dominant_emotion['score']:.1%} confidence]"
                
                # Use Roberto's chat system with emotional context
                enhanced_message = f"{transcription} {emotional_context}"
                response = roberto_instance.chat(enhanced_message)
                
                # Add emotional acknowledgment to response
                emotion_acknowledgments = {
                    "happy": "I can hear the joy in your voice! ",
                    "excited": "Your excitement is contagious! ",
                    "sad": "I sense some sadness in your voice. I'm here for you. ",
                    "angry": "I notice some frustration in your tone. Let's talk through this. ",
                    "neutral": "Thanks for your voice message. ",
                    "thoughtful": "I appreciate the thoughtfulness in your voice. ",
                    "engaged": "I love how engaged you sound! "
                }
                
                acknowledgment = emotion_acknowledgments.get(dominant_emotion['label'], "I received your voice message. ")
                final_response = f"{acknowledgment}{response}"
                
                return final_response, dominant_emotion
            else:
                return f"I received your voice message, though I had some trouble with the transcription. I detected a {dominant_emotion['label']} emotion - how can I help you today?", dominant_emotion
        else:
            return "I received your voice message! While my voice processing is still learning, I'm here to help. What would you like to talk about?", {"label": "neutral", "score": 0.5}
            
    except Exception as e:
        app.logger.error(f"Voice processing error: {e}")
        return "I received your voice message! There was a small hiccup in processing it, but I'm ready to chat. What's on your mind?", {"label": "neutral", "score": 0.5}

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable is required for security")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration with enhanced error handling
database_available = True
try:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
        db.init_app(app)
        
        with app.app_context():
            import models
            db.create_all()
            app.logger.info("Database initialized successfully")
    else:
        database_available = False
        app.logger.info("No database URL, using file-based storage")
        
except Exception as e:
    database_available = False
    app.logger.warning(f"Database unavailable: {e}")
    app.logger.info("Using file-based storage fallback")

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'replit_auth.authorize'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    if database_available:
        try:
            from models import User
            return User.query.get(user_id)
        except:
            return None
    else:
        # Return a minimal user object for file-based mode
        class FileUser:
            def __init__(self, user_id):
                self.id = user_id
                self.is_authenticated = True
                self.is_active = True
                self.is_anonymous = False
            def get_id(self):
                return self.id
        return FileUser(user_id) if user_id else None

@login_manager.unauthorized_handler
def unauthorized():
    from flask import render_template
    return render_template('403.html'), 403

# Register authentication blueprint
try:
    from replit_auth import make_replit_blueprint
    app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")
    app.logger.info("Replit Auth blueprint registered successfully")
except Exception as e:
    app.logger.error(f"Authentication blueprint registration failed: {e}")
    # Authentication is required - do not disable it

# Global Roboto instance
roberto = None

def make_session_permanent():
    """Make session permanent"""
    session.permanent = True

def get_user_roberto():
    """Get or create a Roboto instance for the current user"""
    global roberto
    
    if roberto is None:
        from app1 import Roboto
        from voice_optimization import VoiceOptimizer
        from advanced_learning_engine import AdvancedLearningEngine
        from learning_optimizer import LearningOptimizer
        
        roberto = Roboto()
        
        # Add voice cloning system
        try:
            roberto.voice_cloning = SimpleVoiceCloning("Roberto Villarreal Martinez")
            app.logger.info("Voice cloning system initialized for Roberto Villarreal Martinez")
        except Exception as e:
            app.logger.error(f"Voice cloning initialization error: {e}")
        
        # Add voice optimization
        try:
            roberto.voice_optimizer = VoiceOptimizer("Roberto Villarreal Martinez")
            app.logger.info("Voice optimization system configured for Roberto Villarreal Martinez")
        except Exception as e:
            app.logger.error(f"Voice optimization initialization error: {e}")
        
        # Add advanced learning engine
        try:
            roberto.learning_engine = AdvancedLearningEngine()
            app.logger.info("Advanced learning systems initialized successfully")
        except Exception as e:
            app.logger.error(f"Learning engine initialization error: {e}")
        
        # Add learning optimizer
        try:
            roberto.learning_optimizer = LearningOptimizer()
            app.logger.info("Learning optimization system activated")
        except Exception as e:
            app.logger.error(f"Learning optimizer initialization error: {e}")
        
        # Add advanced voice processor - CRITICAL FIX
        try:
            from advanced_voice_processor import AdvancedVoiceProcessor
            roberto.advanced_voice_processor = AdvancedVoiceProcessor("Roberto Villarreal Martinez")
            app.logger.info("Advanced voice processor with emotion detection initialized")
        except Exception as e:
            app.logger.error(f"Advanced voice processor initialization error: {e}")
        
        app.logger.info("Roboto instance created with enhanced learning algorithms and voice cloning")
        
        # Load user data if authenticated and database available
        if database_available and current_user.is_authenticated:
            try:
                if hasattr(current_user, 'roboto_data') and current_user.roboto_data:
                    user_data = {
                        'chat_history': current_user.roboto_data.chat_history or [],
                        'learned_patterns': current_user.roboto_data.learned_patterns or {},
                        'user_preferences': current_user.roboto_data.user_preferences or {},
                        'emotional_history': current_user.roboto_data.emotional_history or [],
                        'memory_system_data': current_user.roboto_data.memory_system_data or {},
                        'current_emotion': current_user.roboto_data.current_emotion or 'curious',
                        'current_user_name': current_user.roboto_data.current_user_name
                    }
                    roberto.load_user_data(user_data)
                    app.logger.info("User data loaded from database")
            except Exception as e:
                app.logger.warning(f"Could not load user data: {e}")
    
    return roberto

def save_user_data():
    """Save current Roboto state with enhanced learning data"""
    try:
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
            
            # Try database save if available
            if database_available and current_user.is_authenticated:
                try:
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
                    app.logger.info("User data saved to database")
                except Exception as db_error:
                    app.logger.warning(f"Database save failed: {db_error}")
            
            # Always save to file backup
            _save_to_file_backup(user_data)
                
    except Exception as e:
        app.logger.error(f"Critical error saving user data: {e}")

def _save_to_file_backup(user_data):
    """Save user data to file backup"""
    try:
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
    try:
        if database_available and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return redirect(url_for('app_main'))
    except:
        pass
    
    # Provide current_user context for template
    user_context = None
    try:
        if database_available and hasattr(current_user, 'is_authenticated'):
            user_context = current_user
    except:
        pass
    
    return render_template('index.html', current_user=user_context)

@app.route('/app')
@login_required
def app_main():
    make_session_permanent()
    roberto = get_user_roberto()
    return render_template('app.html')

@app.route('/intro')
def intro():
    roberto = get_user_roberto()
    introduction = roberto.introduce()
    return jsonify({"introduction": introduction})

@app.route('/api/chat_history')
@login_required
def get_chat_history():
    try:
        roberto = get_user_roberto()
        return jsonify({
            "success": True,
            "chat_history": getattr(roberto, 'chat_history', [])
        })
    except Exception as e:
        app.logger.error(f"Chat history error: {e}")
        return jsonify({
            "success": False,
            "chat_history": [],
            "error": "Failed to load chat history"
        })

@app.route('/api/history')
@login_required
def get_history():
    try:
        roberto = get_user_roberto()
        return jsonify({
            "success": True,
            "history": getattr(roberto, 'chat_history', [])
        })
    except Exception as e:
        app.logger.error(f"History error: {e}")
        return jsonify({
            "success": False,
            "history": [],
            "error": "Failed to load history"
        })

@app.route('/api/emotional_status')
def get_emotional_status():
    roberto = get_user_roberto()
    return jsonify({
        "success": True,
        "emotion": roberto.current_emotion,
        "current_emotion": roberto.current_emotion,
        "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5),
        "emotional_context": roberto.get_emotional_context()
    })

@app.route('/api/voice-insights')
def get_voice_insights():
    try:
        roberto = get_user_roberto()
        if hasattr(roberto, 'voice_optimizer') and roberto.voice_optimizer:
            insights = roberto.voice_optimizer.get_optimization_insights()
            config = roberto.voice_optimizer.get_voice_optimization_config()
            
            # Generate user-friendly insights
            user_insights = []
            
            # Voice profile strength
            strength = insights.get('voice_profile_strength', 0)
            if strength > 0.8:
                user_insights.append("Voice profile highly optimized for Roberto Villarreal Martinez")
            elif strength > 0.6:
                user_insights.append("Voice recognition adapting well to your speech patterns")
            else:
                user_insights.append("Building personalized voice profile - continue speaking")
            
            # Recognition accuracy
            accuracy = insights.get('recognition_accuracy', 0)
            if accuracy > 0.9:
                user_insights.append("Excellent voice recognition accuracy achieved")
            elif accuracy > 0.8:
                user_insights.append("Good recognition accuracy with room for improvement")
            else:
                user_insights.append("Voice recognition learning your pronunciation patterns")
            
            # Spanish accent adaptation
            user_insights.append("Spanish-English bilingual support active")
            
            return jsonify({
                "success": True,
                "insights": " • ".join(user_insights),
                "detailed_insights": insights,
                "voice_config": config
            })
        else:
            return jsonify({
                "success": True,
                "insights": "Voice optimization system initializing for Roberto Villarreal Martinez"
            })
    except Exception as e:
        app.logger.error(f"Voice insights error: {e}")
        return jsonify({
            "success": False,
            "insights": "Voice optimization in progress"
        })

@app.route('/api/voice-optimization', methods=['POST'])
def optimize_voice():
    try:
        data = request.get_json()
        recognized_text = data.get('recognized_text', '')
        confidence_score = data.get('confidence', 0.0)
        actual_text = data.get('actual_text', None)
        
        roberto = get_user_roberto()
        if hasattr(roberto, 'voice_optimizer') and roberto.voice_optimizer:
            suggestions = roberto.voice_optimizer.analyze_voice_pattern(
                recognized_text, confidence_score, actual_text
            )
            
            # Save voice profile periodically
            import random
            if random.random() < 0.1:  # 10% chance
                roberto.voice_optimizer.save_voice_profile()
            
            return jsonify({
                "success": True,
                "suggestions": suggestions,
                "confidence": confidence_score,
                "optimization_applied": True
            })
        else:
            return jsonify({
                "success": False,
                "message": "Voice optimization system not available"
            })
    except Exception as e:
        app.logger.error(f"Voice optimization error: {e}")
        return jsonify({
            "success": False,
            "message": "Voice optimization failed"
        })

@app.route('/api/voice-cloning-config')
def get_voice_cloning_config():
    try:
        roberto = get_user_roberto()
        if hasattr(roberto, 'voice_cloning') and roberto.voice_cloning:
            config = roberto.voice_cloning.get_voice_config_for_api()
            return jsonify(config)
        else:
            return jsonify({
                "success": True,
                "insights": "Voice cloning system initializing for Roberto Villarreal Martinez",
                "cloning_available": False
            })
    except Exception as e:
        app.logger.error(f"Voice cloning config error: {e}")
        return jsonify({
            "success": False,
            "insights": "Voice cloning system in development",
            "cloning_available": False
        })

@app.route('/api/apply-voice-cloning', methods=['POST'])
def apply_voice_cloning():
    try:
        data = request.get_json()
        text = data.get('text', '')
        emotion = data.get('emotion', 'neutral')
        
        roberto = get_user_roberto()
        if hasattr(roberto, 'voice_cloning') and roberto.voice_cloning:
            # Get TTS parameters for the specified emotion
            tts_settings = roberto.voice_cloning.get_tts_parameters(emotion)
            
            return jsonify({
                "success": True,
                "tts_parameters": tts_settings,
                "voice_applied": True,
                "personalization_strength": 0.85
            })
        else:
            return jsonify({
                "success": False,
                "message": "Voice cloning not available"
            })
    except Exception as e:
        app.logger.error(f"Voice cloning application error: {e}")
        return jsonify({
            "success": False,
            "message": "Voice cloning failed"
        })

@app.route('/api/export_data')
@login_required
def export_data():
    roberto = get_user_roberto()
    
    # Prepare comprehensive export data
    export_data = {
        "roboto_info": {
            "name": roberto.name,
            "creator": roberto.creator,
            "current_emotion": roberto.current_emotion,
            "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5)
        },
        "chat_history": roberto.chat_history,
        "emotional_history": getattr(roberto, 'emotional_history', []),
        "memory_system": {},
        "learning_data": {},
        "optimization_data": {},
        "export_timestamp": datetime.now().isoformat()
    }
    
    # Add memory system data
    if hasattr(roberto, 'memory_system') and roberto.memory_system:
        try:
            export_data["memory_system"] = {
                "total_memories": len(getattr(roberto.memory_system, 'episodic_memories', [])),
                "user_profiles": getattr(roberto.memory_system, 'user_profiles', {}),
                "self_reflections": getattr(roberto.memory_system, 'self_reflections', [])
            }
        except Exception as e:
            app.logger.warning(f"Memory system export error: {e}")
    
    # Add learning engine data
    if hasattr(roberto, 'learning_engine') and roberto.learning_engine:
        try:
            insights = roberto.learning_engine.get_learning_insights()
            export_data["learning_data"] = insights
        except Exception as e:
            app.logger.warning(f"Learning engine export error: {e}")
    
    # Add optimization data
    if hasattr(roberto, 'learning_optimizer') and roberto.learning_optimizer:
        try:
            optimization_insights = roberto.learning_optimizer.get_optimization_insights()
            export_data["optimization_data"] = optimization_insights
        except Exception as e:
            app.logger.warning(f"Learning optimizer export error: {e}")
    
    return jsonify(export_data)

@app.route('/api/set_cookies', methods=['POST'])
def set_cookies():
    """Set cookies for user preferences and data"""
    data = request.get_json()
    response = jsonify({"status": "success"})
    
    for key, value in data.items():
        response.set_cookie(key, str(value), max_age=30*24*60*60)  # 30 days
    
    return response

@app.route('/api/get_cookies')
def get_cookies():
    """Get all available cookies"""
    return jsonify(dict(request.cookies))

@app.route('/api/set_user_data_cookies', methods=['POST'])
def set_user_data_cookies():
    """Set cookies with user conversation and preference data"""
    roberto = get_user_roberto()
    
    user_data = {
        'recent_conversations': len(roberto.chat_history),
        'current_emotion': roberto.current_emotion,
        'last_interaction': datetime.now().isoformat()
    }
    
    response = jsonify({"status": "success", "data": user_data})
    
    for key, value in user_data.items():
        response.set_cookie(f'roboto_{key}', str(value), max_age=7*24*60*60)  # 7 days
    
    return response

@app.route('/api/keep_alive', methods=['POST'])
def keep_alive():
    """Keep session alive - called by service worker"""
    roberto = get_user_roberto()
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "emotion": roberto.current_emotion
    })

@app.route('/api/import_data', methods=['POST'])
@login_required
def import_data():
    roberto = get_user_roberto()
    
    try:
        data = request.get_json()
        
        if 'chat_history' in data:
            roberto.chat_history.extend(data['chat_history'])
        
        if 'emotional_history' in data:
            roberto.emotional_history.extend(data['emotional_history'])
        
        save_user_data()
        
        return jsonify({
            "status": "success",
            "imported_conversations": len(data.get('chat_history', [])),
            "total_conversations": len(roberto.chat_history)
        })
        
    except Exception as e:
        app.logger.error(f"Import error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
@login_required
def handle_file_upload():
    """Handle file uploads including images"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Secure file handling - SECURITY FIX
        if file.content_length and file.content_length > 50 * 1024 * 1024:  # 50MB limit
            return jsonify({"error": "File too large (max 50MB)"}), 413
        
        secure_name = secure_filename(file.filename)
        if not secure_name:
            return jsonify({"error": "Invalid filename"}), 400
            
        # Create temp directory if it doesn't exist
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save file securely
        filename = os.path.join(temp_dir, f"temp_{datetime.now().timestamp()}_{secure_name}")
        file.save(filename)
        
        roberto = get_user_roberto()
        
        # Process based on file type
        if file.filename and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            response_text = f"I can see you've shared an image: {file.filename}. While I can't process images directly yet, I appreciate you wanting to share this with me. Could you describe what's in the image? I'd love to hear about it!"
        elif file.filename and file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.webm', '.flac')):
            # Process voice message with emotion detection
            response_text, detected_emotion = process_voice_message(filename, roberto)
            if detected_emotion:
                roberto.detected_user_emotion = detected_emotion
                # Update Roberto's emotional state based on detected emotion - ENHANCED FIX
                if hasattr(roberto, 'update_emotional_state'):
                    roberto.update_emotional_state(
                        detected_emotion.get('label', 'neutral'), 
                        f"Voice message with {detected_emotion.get('score', 0.5):.1%} confidence"
                    )
                    # Persist the emotional state immediately
                    save_user_data()
                    app.logger.info(f"Updated emotion state to {detected_emotion.get('label')} with confidence {detected_emotion.get('score', 0.5):.1%}")
        else:
            response_text = f"Thank you for sharing the file '{file.filename}'. I'm still learning how to process different file types, but I appreciate you wanting to share this with me. What would you like to tell me about this file?"
        
        # Clean up temporary file
        try:
            os.remove(filename)
        except:
            pass
        
        return jsonify({
            "response": response_text,
            "emotion": roberto.current_emotion
        })
        
    except Exception as e:
        app.logger.error(f"File upload error: {e}")
        return jsonify({"error": "File upload failed"}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        roberto = get_user_roberto()
        
        # Generate response using enhanced learning algorithms
        response = roberto.chat(message)
        
        # Analyze conversation quality if learning systems are available
        conversation_quality = None
        if hasattr(roberto, 'learning_optimizer') and roberto.learning_optimizer:
            try:
                quality_analysis = roberto.learning_optimizer.analyze_conversation_quality(
                    message, response, 
                    user_emotion=getattr(roberto, 'detected_user_emotion', None),
                    context_length=len(roberto.chat_history)
                )
                conversation_quality = quality_analysis
                
                # Update learning metrics
                roberto.learning_optimizer.update_learning_metrics({
                    'user_input': message,
                    'roboto_response': response,
                    'quality_analysis': quality_analysis,
                    'emotion': roberto.current_emotion,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                app.logger.warning(f"Learning analysis error: {e}")
        
        # Save user data periodically
        save_user_data()
        
        response_data = {
            "success": True,
            "response": response,
            "emotion": roberto.current_emotion,
            "emotion_intensity": getattr(roberto, 'emotion_intensity', 0.5),
            "timestamp": datetime.now().isoformat()
        }
        
        if conversation_quality:
            response_data["quality_score"] = conversation_quality.get("overall_quality", 0.5)
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An error occurred while processing your message"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)