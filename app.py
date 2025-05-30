from app1 import Class Roboto # Assuming you have a class Roboto in app1.py
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

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    response = roberto.chat(message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Using 0.0.0.0 for accessibility
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

@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    response = roberto.chat(message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Using 0.0.0.0 for accessibility