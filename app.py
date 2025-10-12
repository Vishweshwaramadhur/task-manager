from flask import Flask, render_template, request, jsonify
import json
import os

# Create Flask application instance
app = Flask(__name__)

# File name where tasks will be stored
TASKS_FILE = 'tasks.json'

def load_tasks():
    """Load tasks from JSON file."""
     # Check if tasks.json file exists
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f) # Convert JSON file content to Python list and return it
        except Exception as e:
            # Handle all errors
            print(f"Error loading tasks: {e}")
            return []
    return []

def save_tasks(tasks):
    """Save tasks to JSON file."""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4) 
        return True
    except Exception as e:
        print(f"Unexpected error saving tasks: {e}")
        return False

# Load all tasks
tasks = load_tasks()

#4 routes as per the requirement

#. List all tasks
@app.route('/')
def home():
    """Render the main page."""
    return render_template('index.html', tasks=tasks)

# This is for inserting the task
@app.route('/add', methods=['POST'])
def add_task():
    """Add a new task."""
    try:
        data = request.get_json() #get_json method that reads the JSON data sent in the request body
        title = data.get('title')
        description = data.get('description')
        
        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Add new task to list
        tasks.append({
            'title': title,
            'description': description,
            'completed': False
        })
        
        save_tasks(tasks)
        return jsonify({'message': 'Task added successfully'}), 201
    except:
        return jsonify({'error': 'Failed to add task'}), 500

@app.route('/toggle/<int:index>', methods=['POST'])
def toggle_task(index):
    """Mark task as complete or incomplete."""
    try:
        if index < 0 or index >= len(tasks):
            return jsonify({'error': 'Task not found'}), 404
        
        # Toggle the completed status
        tasks[index]['completed'] = not tasks[index]['completed']
        save_tasks(tasks)
        
        return jsonify({'message': 'Task updated successfully'}), 200
    except:
        return jsonify({'error': 'Failed to update task'}), 500

@app.route('/delete/<int:index>', methods=['POST'])
def delete_task(index):
    """Delete a task."""
    try:
        if index < 0 or index >= len(tasks):
            return jsonify({'error': 'Task not found'}), 404
        
        # Remove task from list
        tasks.pop(index)
        save_tasks(tasks)
        
        return jsonify({'message': 'Task deleted successfully'}), 200
    except:
        return jsonify({'error': 'Failed to delete task'}), 500

if __name__ == '__main__':
    app.run(debug=True)