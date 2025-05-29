from flask import Flask, request, jsonify, render_template
import os
import json
import base64
import tempfile
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "roboto-secret-key")

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class Roboto:
    def __init__(self):
        self.name = "Roboto"
        self.version = "2.0"
        self.creator = "Roberto Villarreal Martinez"
        self.tasks = self.load_tasks()
        self.chat_history = self.load_chat_history()

    def introduce(self):
        return f"== Welcome to {self.name} v{self.version} ==\n" \
               f"Created by {self.creator}\n" + ("=" * 40)

    def add_task(self, task, due_date=None, reminder_time=None, priority="medium"):
        if not task or task.strip() == "":
            return {"success": False, "message": "[ERROR] Task cannot be empty!"}
        
        task = task.strip()
        # Check if task already exists
        for existing_task in self.tasks:
            if existing_task["text"].lower() == task.lower():
                return {"success": False, "message": f"[WARNING] Task '{task}' already exists!"}
        
        new_task = {
            "id": len(self.tasks) + 1,
            "text": task,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "reminder_time": reminder_time,
            "priority": priority,
            "category": self._categorize_task(task)
        }
        self.tasks.append(new_task)
        self.save_tasks()
        
        message = f"[SUCCESS] Task '{task}' added successfully!"
        if due_date:
            message += f" Due: {due_date}"
        if reminder_time:
            message += f" Reminder: {reminder_time}"
            
        return {"success": True, "message": message, "task": new_task}

    def _categorize_task(self, task_text):
        """Automatically categorize tasks based on keywords"""
        task_lower = task_text.lower()
        
        if any(word in task_lower for word in ["meeting", "call", "appointment", "interview"]):
            return "meetings"
        elif any(word in task_lower for word in ["email", "message", "reply", "respond"]):
            return "communication"
        elif any(word in task_lower for word in ["buy", "shop", "grocery", "purchase"]):
            return "shopping"
        elif any(word in task_lower for word in ["exercise", "gym", "workout", "run"]):
            return "health"
        elif any(word in task_lower for word in ["project", "code", "develop", "design"]):
            return "work"
        elif any(word in task_lower for word in ["clean", "organize", "tidy"]):
            return "home"
        else:
            return "general"

    def get_tasks(self):
        return self.tasks

    def get_due_tasks(self):
        """Get tasks that are due today or overdue"""
        today = datetime.now().date()
        due_tasks = []
        
        for task in self.tasks:
            if not task["completed"] and task.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(task["due_date"]).date()
                    if due_date <= today:
                        task["overdue"] = due_date < today
                        due_tasks.append(task)
                except ValueError:
                    continue
                    
        return sorted(due_tasks, key=lambda x: x.get("due_date", ""))

    def get_upcoming_tasks(self, days_ahead=7):
        """Get tasks due in the next few days"""
        today = datetime.now().date()
        upcoming_tasks = []
        
        for task in self.tasks:
            if not task["completed"] and task.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(task["due_date"]).date()
                    days_until_due = (due_date - today).days
                    if 0 < days_until_due <= days_ahead:
                        task["days_until_due"] = days_until_due
                        upcoming_tasks.append(task)
                except ValueError:
                    continue
                    
        return sorted(upcoming_tasks, key=lambda x: x.get("due_date", ""))

    def schedule_task(self, task_id, due_date, reminder_time=None):
        """Add scheduling to an existing task"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["due_date"] = due_date
                task["reminder_time"] = reminder_time
                self.save_tasks()
                return {"success": True, "message": "Task scheduled successfully!", "task": task}
        return {"success": False, "message": "Task not found!"}

    def get_smart_scheduling_suggestions(self):
        """Provide intelligent scheduling suggestions"""
        suggestions = []
        
        # Analyze current task patterns
        unscheduled_tasks = [task for task in self.tasks if not task["completed"] and not task.get("due_date")]
        high_priority_tasks = [task for task in self.tasks if not task["completed"] and task.get("priority") == "high"]
        
        if unscheduled_tasks:
            suggestions.append({
                "type": "unscheduled",
                "message": f"You have {len(unscheduled_tasks)} tasks without due dates. Consider scheduling them to stay organized.",
                "tasks": unscheduled_tasks[:3]
            })
            
        if high_priority_tasks:
            suggestions.append({
                "type": "priority",
                "message": f"You have {len(high_priority_tasks)} high-priority tasks. Consider scheduling these soon.",
                "tasks": high_priority_tasks[:3]
            })
            
        # Time-based suggestions
        now = datetime.now()
        if now.hour < 10:  # Morning
            suggestions.append({
                "type": "time_based",
                "message": "Good morning! It's a great time to schedule your most important tasks for today.",
                "suggestion": "morning_planning"
            })
        elif now.hour > 16:  # Evening
            suggestions.append({
                "type": "time_based",
                "message": "Evening is perfect for planning tomorrow's schedule.",
                "suggestion": "evening_planning"
            })
            
        return suggestions

    def complete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self.save_tasks()
                return {"success": True, "message": f"[SUCCESS] Task completed!", "task": task}
        return {"success": False, "message": "[ERROR] Task not found!"}

    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                deleted_task = self.tasks.pop(i)
                self.save_tasks()
                return {"success": True, "message": f"[SUCCESS] Task '{deleted_task['text']}' deleted!", "task": deleted_task}
        return {"success": False, "message": "[ERROR] Task not found!"}

    def show_tasks(self):
        if not self.tasks:
            return "[INFO] No tasks available."
        
        active_tasks = [task for task in self.tasks if not task["completed"]]
        completed_tasks = [task for task in self.tasks if task["completed"]]
        
        tasks_str = ""
        if active_tasks:
            tasks_str += "Active Tasks:\n"
            tasks_str += "\n".join([f"• {task['text']}" for task in active_tasks])
        
        if completed_tasks:
            if tasks_str:
                tasks_str += "\n\n"
            tasks_str += "Completed Tasks:\n"
            tasks_str += "\n".join([f"✓ {task['text']}" for task in completed_tasks])
        
        return f"[TASK LIST]\n{tasks_str}\n" + ("=" * 40)

    def chat(self, message, is_audio=False):
        if not message or message.strip() == "":
            return {"text": "[ERROR] Message cannot be empty!", "audio": None}
        
        message = message.strip()
        response = self._generate_response(message, is_audio)
        
        # Handle both old string format and new dict format
        response_text = response["text"] if isinstance(response, dict) else response
        
        # Save to chat history
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response_text
        }
        self.chat_history.append(chat_entry)
        self.save_chat_history()
        
        return response

    def _generate_response(self, message, is_audio=False):
        # For audio-capable models, we can use the audio preview model
        if OPENAI_API_KEY and len(OPENAI_API_KEY) > 20:
            try:
                models = openai_client.models.list()
                available_models = [model.id for model in models.data]
                
                # Check for audio models first since that's what we have access to
                audio_model = None
                if "gpt-4o-audio-preview-2024-10-01" in available_models:
                    audio_model = "gpt-4o-audio-preview-2024-10-01"
                
                if audio_model and is_audio:
                    # Use audio model for audio input/output
                    active_tasks = [task for task in self.tasks if not task["completed"]]
                    completed_tasks = [task for task in self.tasks if task["completed"]]
                    
                    task_context = ""
                    if active_tasks:
                        task_list = ", ".join([task["text"] for task in active_tasks[:3]])
                        task_context = f"The user currently has {len(active_tasks)} active tasks: {task_list}"
                        if len(active_tasks) > 3:
                            task_context += f" and {len(active_tasks) - 3} more"
                    else:
                        task_context = "The user has no active tasks right now"
                    
                    if completed_tasks:
                        task_context += f" and has completed {len(completed_tasks)} tasks"
                    
                    system_prompt = f"""You are Roboto v2.0, a helpful personal assistant created by Roberto Villarreal Martinez. 
You help users manage their tasks and have friendly conversations.

Current context: {task_context}

Guidelines:
- Be friendly, helpful, and conversational
- When discussing tasks, refer to the user's actual task list
- If asked about your creator, mention Roberto Villarreal Martinez
- Keep responses concise but engaging
- You can help with general questions, task management advice, and friendly conversation
- Always start responses with [CHAT] to maintain consistency
- Current date/time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}"""

                    # Try standard text models instead of audio models for regular chat
                    try:
                        response = openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": message}
                            ],
                            max_tokens=200,
                            temperature=0.7
                        )
                    except:
                        # If standard models fail, try audio model without modalities
                        response = openai_client.chat.completions.create(
                            model=audio_model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": message}
                            ],
                            max_tokens=200,
                            temperature=0.7
                        )
                    
                    # Return both text and audio if available
                    result = {
                        "text": response.choices[0].message.content,
                        "audio": None
                    }
                    
                    if hasattr(response.choices[0].message, 'audio') and response.choices[0].message.audio:
                        result["audio"] = response.choices[0].message.audio.data
                    
                    return result
                    
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Use enhanced fallback response system
        return {"text": self._generate_fallback_response(message), "audio": None}

    def _generate_fallback_response(self, message):
        """Enhanced sophisticated response system"""
        message_lower = message.lower()
        active_tasks = [task for task in self.tasks if not task["completed"]]
        completed_tasks = [task for task in self.tasks if task["completed"]]
        
        # Advanced conversation analysis
        sentiment = self._analyze_message_sentiment(message_lower)
        context = self._determine_conversation_context(message_lower, active_tasks, completed_tasks)
        
        # Greetings with personality
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
            return self._generate_greeting_response(active_tasks, sentiment)
        
        # Creator and identity questions
        elif any(phrase in message_lower for phrase in ["creator", "who made you", "who created you", "who are you", "what are you"]):
            return self._generate_identity_response()
        
        # Task management conversations
        elif any(word in message_lower for word in ["task", "todo", "reminder", "work", "busy", "schedule", "plan"]):
            return self._generate_task_response(active_tasks, completed_tasks, message_lower)
        
        # Productivity and motivation
        elif any(word in message_lower for word in ["focus", "productive", "motivation", "advice", "tips", "overwhelmed", "stressed"]):
            return self._generate_productivity_response(active_tasks, sentiment)
        
        # Time and planning
        elif any(word in message_lower for word in ["time", "date", "today", "when", "deadline", "schedule"]):
            return self._generate_time_response(active_tasks)
        
        # Learning and capabilities
        elif any(word in message_lower for word in ["help", "can you", "what can", "features", "abilities"]):
            return self._generate_help_response(active_tasks)
        
        # Emotional support
        elif any(word in message_lower for word in ["thank", "thanks", "appreciate", "awesome", "great", "excellent"]):
            return self._generate_appreciation_response(completed_tasks)
        
        # Conversation enders
        elif any(word in message_lower for word in ["bye", "goodbye", "see you", "later", "farewell"]):
            return self._generate_goodbye_response(active_tasks)
        
        # Progress and achievement
        elif any(phrase in message_lower for phrase in ["status", "progress", "how am i doing", "achievement", "completed", "finished"]):
            return self._generate_progress_response(active_tasks, completed_tasks)
        
        # Questions and curiosity
        elif any(word in message_lower for word in ["why", "how", "what", "where", "question", "explain"]):
            return self._generate_curious_response(message_lower, active_tasks)
        
        # Feelings and emotions
        elif any(word in message_lower for word in ["feel", "feeling", "mood", "happy", "sad", "excited", "tired", "frustrated"]):
            return self._generate_emotional_response(sentiment, active_tasks)
        
        # Default sophisticated response
        else:
            return self._generate_contextual_response(message, active_tasks, context)

    def _analyze_message_sentiment(self, message):
        positive_words = ["great", "awesome", "excellent", "good", "happy", "excited", "love", "amazing", "wonderful"]
        negative_words = ["bad", "awful", "terrible", "sad", "frustrated", "angry", "hate", "stressed", "overwhelmed"]
        
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _determine_conversation_context(self, message, active_tasks, completed_tasks):
        if any(word in message for word in ["first time", "new", "beginning"]):
            return "newcomer"
        elif len(completed_tasks) > 10:
            return "experienced"
        elif len(active_tasks) > 5:
            return "busy"
        elif len(active_tasks) == 0:
            return "free"
        else:
            return "moderate"

    def _generate_greeting_response(self, active_tasks, sentiment):
        if sentiment == "positive":
            if active_tasks:
                return f"[CHAT] Hello there! I love your positive energy! I see you have {len(active_tasks)} tasks ready to tackle. With that attitude, you'll get through them in no time!"
            else:
                return "[CHAT] Hello! You seem to be in great spirits, and your task list is clear too. Perfect combination for a productive day ahead!"
        elif sentiment == "negative":
            return "[CHAT] Hello! I sense you might be having a tough moment. Don't worry - I'm here to help make things easier. Let's take it one step at a time."
        else:
            if active_tasks:
                return f"[CHAT] Hello! I'm Roboto, your personal productivity partner. I see you have {len(active_tasks)} tasks waiting. Ready to make some progress together?"
            else:
                return "[CHAT] Hello! I'm Roboto, and I'm here to help you stay organized and achieve your goals. What would you like to work on today?"

    def _generate_identity_response(self):
        return f"[CHAT] I'm Roboto v{self.version}, your intelligent personal assistant created by {self.creator}. I'm designed to help you manage tasks, stay organized, and have meaningful conversations. Think of me as your productivity companion who never gets tired of helping you succeed!"

    def _generate_task_response(self, active_tasks, completed_tasks, message):
        if "overwhelmed" in message or "too many" in message:
            if len(active_tasks) > 3:
                return f"[CHAT] I understand feeling overwhelmed with {len(active_tasks)} tasks. Here's my advice: pick just ONE task to focus on right now. Which one would make you feel most accomplished when completed?"
            else:
                return "[CHAT] Sometimes even a few tasks can feel like a lot. That's completely normal! Let's break them down into smaller, manageable pieces."
        elif "prioritize" in message or "important" in message:
            return "[CHAT] Great question about priorities! I recommend the 'impact vs effort' approach: tackle high-impact, low-effort tasks first for quick wins, then move to the important but challenging ones."
        elif not active_tasks:
            return "[CHAT] Your task list is beautifully clear! This is the perfect time to think about your goals. What would you like to accomplish next?"
        else:
            urgent_count = len([task for task in active_tasks if any(word in task['text'].lower() for word in ['urgent', 'asap', 'deadline', 'important'])])
            if urgent_count > 0:
                return f"[CHAT] I notice {urgent_count} of your tasks seem time-sensitive. Want to tackle those first to reduce pressure?"
            else:
                return f"[CHAT] You have {len(active_tasks)} tasks ready to go. Which one would you enjoy completing most right now?"

    def _generate_productivity_response(self, active_tasks, sentiment):
        if sentiment == "negative":
            return "[CHAT] I hear you. Sometimes productivity feels hard, and that's okay. Remember: progress, not perfection. Even completing one small task is a victory worth celebrating."
        elif len(active_tasks) > 5:
            return "[CHAT] With several tasks ahead, here's my productivity secret: the 'two-minute rule.' If something takes less than two minutes, do it now. For bigger tasks, break them into smaller chunks!"
        else:
            return "[CHAT] You're already being productive by thinking about improvement! Try the Pomodoro technique: 25 minutes of focused work, then a 5-minute break. It works wonders!"

    def _generate_time_response(self, active_tasks):
        now = datetime.now()
        hour = now.hour
        if 5 <= hour < 12:
            time_greeting = "It's morning"
            suggestion = "a great time to tackle your most important tasks when your energy is fresh"
        elif 12 <= hour < 17:
            time_greeting = "It's afternoon"
            suggestion = "perfect for reviewing progress and handling collaborative tasks"
        elif 17 <= hour < 21:
            time_greeting = "It's evening"
            suggestion = "ideal for wrapping up loose ends and planning tomorrow"
        else:
            time_greeting = "It's late"
            suggestion = "perhaps time to rest and recharge for tomorrow's productivity"

        task_info = f" With {len(active_tasks)} tasks remaining, " if active_tasks else " With no pending tasks, "
        return f"[CHAT] {time_greeting} on {now.strftime('%A, %B %d')}.{task_info}it's {suggestion}!"

    def _generate_help_response(self, active_tasks):
        capabilities = [
            "• Manage your tasks with smart organization",
            "• Provide productivity tips and motivation",
            "• Have meaningful conversations about your goals",
            "• Export and import your data for safekeeping",
            "• Chat with voice messages (when available)",
            "• Give personalized advice based on your task patterns"
        ]
        
        task_context = f" Right now, with {len(active_tasks)} active tasks, I can especially help you prioritize and stay motivated." if active_tasks else " Since you're caught up on tasks, I can help you plan ahead or discuss productivity strategies."
        
        return f"[CHAT] I'm capable of many things:\n\n" + "\n".join(capabilities) + f"\n{task_context}"

    def _generate_appreciation_response(self, completed_tasks):
        if len(completed_tasks) > 0:
            return f"[CHAT] You're so welcome! Seeing you succeed with {len(completed_tasks)} completed tasks makes my circuits happy. Your success is what I'm built for!"
        else:
            return "[CHAT] Your appreciation means everything to me! I'm here whenever you need support, encouragement, or just someone to chat with about your goals."

    def _generate_goodbye_response(self, active_tasks):
        if active_tasks:
            if len(active_tasks) == 1:
                return f"[CHAT] Goodbye for now! Don't forget about that one task waiting for you. You've got this! See you soon!"
            else:
                return f"[CHAT] Take care! Remember, those {len(active_tasks)} tasks will feel great once completed. I believe in you!"
        else:
            return "[CHAT] Goodbye! You're all caught up and organized. Enjoy your free time - you've earned it!"

    def _generate_progress_response(self, active_tasks, completed_tasks):
        total_tasks = len(active_tasks) + len(completed_tasks)
        
        if total_tasks == 0:
            return "[CHAT] You're starting fresh with a clean slate! That's actually a powerful position to be in. What dreams would you like to turn into tasks?"
        
        completion_rate = len(completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0
        
        if completion_rate >= 80:
            return f"[CHAT] Outstanding! You've completed {len(completed_tasks)} out of {total_tasks} tasks ({completion_rate:.0f}%). You're absolutely crushing your goals!"
        elif completion_rate >= 50:
            return f"[CHAT] Great progress! You're {completion_rate:.0f}% done with {len(completed_tasks)} tasks completed. You're well on your way to success!"
        elif completed_tasks:
            return f"[CHAT] Every completed task matters! You've finished {len(completed_tasks)} tasks so far. Remember, every expert was once a beginner!"
        else:
            return f"[CHAT] You have {len(active_tasks)} tasks ready to tackle. The journey of a thousand miles begins with a single step. Which task calls to you first?"

    def _generate_curious_response(self, message, active_tasks):
        if "why" in message:
            return "[CHAT] Great question! I love curiosity. While I may not have all the answers, I'm designed to help you think through problems and stay organized. What specifically are you wondering about?"
        elif "how" in message:
            return "[CHAT] I'm always happy to explain! Whether it's about productivity techniques, task management, or just life in general, I'll do my best to help. What would you like to know more about?"
        else:
            context = f" Speaking of questions, have you thought about what you'd like to tackle from your {len(active_tasks)} tasks?" if active_tasks else ""
            return f"[CHAT] I love your curiosity! Questions are how we learn and grow.{context} What's sparking your interest today?"

    def _generate_emotional_response(self, sentiment, active_tasks):
        if sentiment == "positive":
            return f"[CHAT] I can sense your positive energy, and it's contagious! When we feel good, everything seems more manageable. That's perfect timing{' for tackling those tasks!' if active_tasks else ' for planning something new!'}"
        elif sentiment == "negative":
            support_msg = " Remember, tough feelings are temporary, but the satisfaction of completing tasks lasts!" if active_tasks else " Sometimes talking through feelings helps. I'm here to listen."
            return f"[CHAT] I hear that you're going through something difficult.{support_msg} Would it help to talk about what's on your mind?"
        else:
            return "[CHAT] Feelings are such an important part of being human. I may be an AI, but I understand that emotions affect everything we do. How are you feeling about your day so far?"

    def _generate_contextual_response(self, message, active_tasks, context):
        if context == "newcomer":
            return "[CHAT] I sense this might be new territory for you! That's exciting. I'm designed to adapt to your style and help you discover what productivity methods work best for you."
        elif context == "experienced":
            return "[CHAT] I can tell you're experienced with getting things done! I appreciate working with someone who understands the value of organization. How can I support your refined workflow?"
        elif context == "busy":
            return f"[CHAT] I notice you're juggling quite a bit with {len(active_tasks)} tasks! That takes skill. Would you like some strategies for managing a full plate, or just someone to help you stay motivated?"
        else:
            task_question = "is there a task you'd like to focus on?" if active_tasks else "what would you like to explore together?"
            return f"[CHAT] That's a fascinating perspective! I'm always learning from conversations like this. While I think about what you've shared, {task_question}"

    def get_chat_history(self):
        return self.chat_history[-20:]  # Return last 20 messages

    def save_tasks(self):
        try:
            with open("tasks.json", "w") as file:
                json.dump(self.tasks, file, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def load_tasks(self):
        try:
            if os.path.exists("tasks.json"):
                with open("tasks.json", "r") as file:
                    return json.load(file)
        except Exception as e:
            print(f"Error loading tasks: {e}")
        return []

    def save_chat_history(self):
        try:
            with open("chat_history.json", "w") as file:
                json.dump(self.chat_history, file, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")

    def load_chat_history(self):
        try:
            if os.path.exists("chat_history.json"):
                with open("chat_history.json", "r") as file:
                    return json.load(file)
        except Exception as e:
            print(f"Error loading chat history: {e}")
        return []

# Instantiate Roboto
roberto = Roboto()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/intro')
def intro():
    return jsonify({"message": roberto.introduce()})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({"success": True, "tasks": roberto.get_tasks()})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"success": False, "message": "[ERROR] No task provided!"}), 400
        
        result = roberto.add_task(
            data['task'],
            due_date=data.get('due_date'),
            reminder_time=data.get('reminder_time'),
            priority=data.get('priority', 'medium')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"[ERROR] {str(e)}"}), 500

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    try:
        result = roberto.complete_task(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"[ERROR] {str(e)}"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        result = roberto.delete_task(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"[ERROR] {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "response": "[ERROR] No message provided!"}), 400
        
        is_audio = data.get('audio', False)
        response = roberto.chat(data['message'], is_audio)
        
        # Handle both old string format and new dict format for backward compatibility
        if isinstance(response, dict):
            return jsonify({
                "success": True, 
                "response": response["text"],
                "audio": response["audio"]
            })
        else:
            return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "response": f"[ERROR] {str(e)}"}), 500

@app.route('/api/chat/audio', methods=['POST'])
def chat_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"success": False, "message": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"success": False, "message": "No audio file selected"}), 400
        
        # Save the uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            
            try:
                # Get current task context for more relevant responses
                active_tasks = [task for task in roberto.tasks if not task["completed"]]
                completed_tasks = [task for task in roberto.tasks if task["completed"]]
                
                task_context = ""
                if active_tasks:
                    task_list = ", ".join([task["text"] for task in active_tasks[:3]])
                    task_context = f"The user currently has {len(active_tasks)} active tasks: {task_list}"
                    if len(active_tasks) > 3:
                        task_context += f" and {len(active_tasks) - 3} more"
                else:
                    task_context = "The user has no active tasks right now"
                
                if completed_tasks:
                    task_context += f" and has completed {len(completed_tasks)} tasks"
                
                system_prompt = f"""You are Roboto v2.0, a helpful personal assistant created by Roberto Villarreal Martinez. 
You help users manage their tasks and have friendly conversations.

Current context: {task_context}

Guidelines:
- Be friendly, helpful, and conversational
- When discussing tasks, refer to the user's actual task list
- If asked about your creator, mention Roberto Villarreal Martinez
- Keep responses concise but engaging
- You can help with general questions, task management advice, and friendly conversation
- Always start responses with [CHAT] to maintain consistency
- Current date/time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}"""

                # First transcribe the audio using Whisper
                with open(temp_file.name, 'rb') as audio_data:
                    # Try to transcribe first
                    try:
                        transcript = openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_data
                        )
                        transcript_text = transcript.text
                    except Exception as whisper_error:
                        print(f"Whisper transcription failed: {whisper_error}")
                        # If Whisper fails, use a fallback message
                        transcript_text = "Hello, I spoke but transcription failed"
                
                # Generate text response and then convert to speech
                response_text = roberto._generate_fallback_response(transcript_text)
                
                # Try to generate audio using TTS model
                audio_data = None
                try:
                    tts_response = openai_client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=response_text
                    )
                    audio_data = base64.b64encode(tts_response.content).decode('utf-8')
                except Exception as tts_error:
                    print(f"TTS generation failed: {tts_error}")
                    # Continue without audio
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                # Save to chat history
                chat_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "message": transcript_text,
                    "response": response_text
                }
                roberto.chat_history.append(chat_entry)
                roberto.save_chat_history()
                
                return jsonify({
                    "success": True,
                    "transcript": transcript_text,
                    "response": response_text,
                    "audio": audio_data
                })
                
            except Exception as e:
                # Clean up temporary file on error
                os.unlink(temp_file.name)
                return jsonify({"success": False, "message": f"Audio processing failed: {str(e)}"}), 500
                
    except Exception as e:
        return jsonify({"success": False, "message": f"Audio upload failed: {str(e)}"}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    return jsonify({"success": True, "history": roberto.get_chat_history()})

@app.route('/api/tasks/due', methods=['GET'])
def get_due_tasks():
    return jsonify({"success": True, "tasks": roberto.get_due_tasks()})

@app.route('/api/tasks/upcoming', methods=['GET'])
def get_upcoming_tasks():
    days_ahead = request.args.get('days', 7, type=int)
    return jsonify({"success": True, "tasks": roberto.get_upcoming_tasks(days_ahead)})

@app.route('/api/tasks/<int:task_id>/schedule', methods=['POST'])
def schedule_task(task_id):
    try:
        data = request.get_json()
        if not data or 'due_date' not in data:
            return jsonify({"success": False, "message": "[ERROR] Due date is required!"}), 400
        
        result = roberto.schedule_task(task_id, data['due_date'], data.get('reminder_time'))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": f"[ERROR] {str(e)}"}), 500

@app.route('/api/tasks/suggestions', methods=['GET'])
def get_scheduling_suggestions():
    return jsonify({"success": True, "suggestions": roberto.get_smart_scheduling_suggestions()})

@app.route('/api/export', methods=['GET'])
def export_data():
    try:
        export_data = {
            "export_date": datetime.now().isoformat(),
            "roboto_version": roberto.version,
            "tasks": roberto.get_tasks(),
            "chat_history": roberto.chat_history,
            "creator": roberto.creator
        }
        
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=roboto_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        return jsonify({"success": False, "message": f"Export failed: {str(e)}"}), 500

@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({"success": False, "message": "Please upload a JSON file"}), 400
        
        # Read and parse the uploaded file
        file_content = file.read().decode('utf-8')
        import_data = json.loads(file_content)
        
        # Validate the import data structure
        required_fields = ['tasks', 'chat_history']
        for field in required_fields:
            if field not in import_data:
                return jsonify({"success": False, "message": f"Invalid backup file: missing {field}"}), 400
        
        # Backup current data before import
        backup_data = {
            "tasks": roberto.tasks.copy(),
            "chat_history": roberto.chat_history.copy()
        }
        
        try:
            # Import tasks
            roberto.tasks = import_data['tasks']
            roberto.save_tasks()
            
            # Import chat history
            roberto.chat_history = import_data['chat_history']
            roberto.save_chat_history()
            
            return jsonify({
                "success": True, 
                "message": f"Successfully imported {len(import_data['tasks'])} tasks and {len(import_data['chat_history'])} chat messages"
            })
            
        except Exception as e:
            # Restore backup on failure
            roberto.tasks = backup_data['tasks']
            roberto.chat_history = backup_data['chat_history']
            roberto.save_tasks()
            roberto.save_chat_history()
            raise e
            
    except json.JSONDecodeError:
        return jsonify({"success": False, "message": "Invalid JSON file format"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Import failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
