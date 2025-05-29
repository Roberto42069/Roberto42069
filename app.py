from flask import Flask, request, jsonify, render_template
import os
import json
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

    def add_task(self, task):
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
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(new_task)
        self.save_tasks()
        return {"success": True, "message": f"[SUCCESS] Task '{task}' added successfully!", "task": new_task}

    def get_tasks(self):
        return self.tasks

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

    def chat(self, message):
        if not message or message.strip() == "":
            return "[ERROR] Message cannot be empty!"
        
        message = message.strip()
        response = self._generate_response(message)
        
        # Save to chat history
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response
        }
        self.chat_history.append(chat_entry)
        self.save_chat_history()
        
        return response

    def _generate_response(self, message):
        try:
            # Get current task context for more relevant responses
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
            
            # Create system prompt
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

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Enhanced fallback response system
            return self._generate_fallback_response(message)

    def _generate_fallback_response(self, message):
        """Enhanced fallback response system when OpenAI API is unavailable"""
        message_lower = message.lower()
        active_tasks = [task for task in self.tasks if not task["completed"]]
        completed_tasks = [task for task in self.tasks if task["completed"]]
        
        # Greetings
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            if active_tasks:
                return f"[CHAT] Hello! I'm Roboto, your personal assistant. I see you have {len(active_tasks)} active tasks to work on. How can I help you stay productive today?"
            else:
                return "[CHAT] Hello! I'm Roboto, your personal assistant. You're all caught up with tasks - great work! What would you like to chat about?"
        
        # Creator questions
        elif any(phrase in message_lower for phrase in ["creator", "who made you", "who created you"]):
            return f"[CHAT] I was created by {self.creator}. He's a talented developer who built me to help people stay organized and productive!"
        
        # Task-related queries
        elif any(word in message_lower for word in ["task", "todo", "reminder", "work", "busy"]):
            if not active_tasks:
                return "[CHAT] You don't have any active tasks right now. Would you like to add one? I'm here to help you stay organized!"
            elif len(active_tasks) == 1:
                return f"[CHAT] You have 1 active task: '{active_tasks[0]['text']}'. Keep up the good work!"
            else:
                task_preview = active_tasks[0]['text']
                return f"[CHAT] You have {len(active_tasks)} active tasks. Your first one is '{task_preview}'. Would you like to focus on completing that first?"
        
        # Productivity and motivation
        elif any(word in message_lower for word in ["focus", "productive", "motivation", "advice"]):
            if active_tasks:
                return f"[CHAT] Great question! With {len(active_tasks)} tasks on your list, I'd suggest starting with the most important one. Breaking big tasks into smaller steps can help too!"
            else:
                return "[CHAT] You're doing great! Since you don't have any pending tasks, this might be a good time to plan ahead or take a well-deserved break."
        
        # Time/date queries
        elif any(word in message_lower for word in ["time", "date", "today", "when"]):
            now = datetime.now()
            task_info = f" You have {len(active_tasks)} active tasks" if active_tasks else " You're all caught up with tasks"
            return f"[CHAT] Today is {now.strftime('%A, %B %d, %Y')} and it's {now.strftime('%I:%M %p')}.{task_info}!"
        
        # Help
        elif "help" in message_lower:
            return "[CHAT] I can help you manage tasks, provide productivity advice, and have friendly conversations. Try asking me about your tasks, time management, or just say hello!"
        
        # Thank you
        elif any(word in message_lower for word in ["thank", "thanks"]):
            return "[CHAT] You're very welcome! I'm always here to help you stay organized and productive. Keep up the great work!"
        
        # Goodbye
        elif any(word in message_lower for word in ["bye", "goodbye", "see you"]):
            reminder = f" Don't forget about your {len(active_tasks)} active tasks!" if active_tasks else " Keep up the excellent work!"
            return f"[CHAT] Goodbye! It was great chatting with you.{reminder}"
        
        # Status check
        elif any(word in message_lower for word in ["status", "progress", "how am i doing"]):
            if completed_tasks and active_tasks:
                return f"[CHAT] You're doing well! You've completed {len(completed_tasks)} tasks and have {len(active_tasks)} remaining. That's solid progress!"
            elif completed_tasks and not active_tasks:
                return f"[CHAT] Excellent! You've completed {len(completed_tasks)} tasks and have nothing pending. You're crushing it!"
            elif active_tasks and not completed_tasks:
                return f"[CHAT] You have {len(active_tasks)} tasks to work on. Every journey starts with a single step - let's get started!"
            else:
                return "[CHAT] Your task list is clean! This is a perfect time to add new goals or enjoy your productivity."
        
        # Default response
        else:
            if active_tasks:
                return f"[CHAT] That's interesting! I'm still learning to respond to everything, but I notice you have {len(active_tasks)} tasks pending. Need help prioritizing them?"
            else:
                return "[CHAT] I find that fascinating! While I continue learning new topics, I'm here to help with task management and productivity. What's on your mind?"

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
        
        result = roberto.add_task(data['task'])
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
        
        response = roberto.chat(data['message'])
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "response": f"[ERROR] {str(e)}"}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    return jsonify({"success": True, "history": roberto.get_chat_history()})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
