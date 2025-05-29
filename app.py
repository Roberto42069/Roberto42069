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
            # Fallback to basic response if API fails
            return f"[CHAT] I'm having trouble connecting to my AI brain right now, but I'm still here to help! You currently have {len([task for task in self.tasks if not task['completed']])} active tasks."

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
