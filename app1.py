import json
import os
from openai import OpenAI


class Roboto:

    def __init__(self):
        self.name = "Roboto"
        self.version = "1.0"
        self.creator = "Roberto Villarreal Martinez"
        self.tasks = self.load_tasks()
        self.chat_history = self.load_chat_history()
        self.learned_patterns = {}
        self.user_preferences = {}
        self.conversation_context = {}
        self.conversation_memory = []
        self.user_emotional_state = "neutral"
        self.user_quirks = []
        self.load_grok_chat_data()
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def load_grok_chat_data(self):
        try:
            with open("attached_assets/grok-chat-item.js", "r") as file:
                grok_data = json.load(file)
                for item in grok_data['part0']:
                    message = item['grokChatItem']['message']
                    sender = item['grokChatItem']['sender']['name']
                    self.chat_history.append({
                        "sender": sender,
                        "message": message
                    })
        except Exception as e:
            print(f"Error loading Grok chat data: {e}")

    def load_tasks(self):
        if os.path.exists("tasks.txt"):
            with open("tasks.txt", "r") as file:
                tasks = file.read().splitlines()
            return tasks
        return []

    def load_chat_history(self):
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r") as file:
                return json.load(file)
        return []

    def introduce(self):
        return f"== Welcome to {self.name} v{self.version} ==\n" \
               f"Created by {self.creator}\n" + ("=" * 40)

    def show_tasks(self):
        """Return list of tasks in the expected format for the frontend"""
        task_list = []
        for i, task in enumerate(self.tasks):
            task_list.append({
                "id": i,
                "text": task,
                "completed": False
            })
        return task_list

    def add_task(self, task_text):
        """Add a new task"""
        try:
            self.tasks.append(task_text)
            self.save_tasks()
            return {"success": True, "message": "Task added successfully!"}
        except Exception as e:
            return {"success": False, "message": f"Error adding task: {str(e)}"}

    def save_tasks(self):
        """Save tasks to file"""
        with open("tasks.txt", "w") as file:
            for task in self.tasks:
                file.write(task + "\n")

    def chat(self, message):
        """Handle chat messages"""
        if not message:
            return "Please provide a message to chat."
        
        # Store the user message
        chat_entry = {
            "message": message,
            "response": "",
            "timestamp": ""
        }
        
        # Simple response logic (you can enhance this with OpenAI later)
        response = self.generate_response(message)
        chat_entry["response"] = response
        
        # Add to chat history
        self.chat_history.append(chat_entry)
        self.save_chat_history()
        
        return response

    def generate_response(self, message):
        """Generate a response to user message using OpenAI"""
        try:
            # Build context from recent conversation history
            context_messages = [
                {"role": "system", "content": f"You are {self.name}, a helpful personal assistant created by {self.creator}. You help users with task management, conversations, and provide intelligent assistance. Keep responses conversational and helpful."}
            ]
            
            # Add recent chat history for context (last 5 messages)
            recent_history = self.chat_history[-5:] if len(self.chat_history) > 5 else self.chat_history
            for entry in recent_history:
                if 'message' in entry and 'response' in entry:
                    context_messages.append({"role": "user", "content": entry['message']})
                    context_messages.append({"role": "assistant", "content": entry['response']})
            
            # Add current message
            context_messages.append({"role": "user", "content": message})
            
            # Call OpenAI API with a more widely available model
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context_messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to simple response if OpenAI fails
            return self.simple_response(message)
    
    def simple_response(self, message):
        """Simple fallback response when OpenAI is unavailable"""
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm Roboto, your personal assistant. How can I help you today?"
        elif "task" in message_lower:
            return "I can help you manage your tasks! You can add new tasks or view your current ones."
        elif "help" in message_lower:
            return "I can help you with task management, answer questions, and have conversations. What would you like to do?"
        else:
            return "That's interesting! I'm still learning. Is there anything specific I can help you with?"

    def save_chat_history(self):
        """Save chat history to file"""
        with open("chat_history.json", "w") as file:
            json.dump(self.chat_history, file, indent=2)
