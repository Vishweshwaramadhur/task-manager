# Task Manager Application

A simple web-based task manager built with Flask, HTML, CSS, and JavaScript.

## Implementation Approach

- **Backend**: Used Flask framework to create REST API endpoints for adding, toggling, and deleting tasks
- **Frontend**: Built with HTML, CSS, and JavaScript. JavaScript uses `fetch()` API to communicate with the backend
- **Data Storage**: Tasks are stored in `tasks.json` file. The file is loaded on app startup and saved after every operation
- **Error Handling**: Added try-except blocks to handle JSON errors and invalid requests

## Features

- ✅ Add new tasks with title and description
- ✅ Mark tasks as complete/incomplete
- ✅ Delete tasks
- ✅ View all tasks in a list
- ✅ Data saved in JSON file

## Requirements

- Python 3.x (tested on Python 3.12.3)
- Flask

## Project Structure

```
task-manager/
├── app.py                # Main Flask application
├── tasks.json            # Task data (created automatically)
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Styling
│   └── script.js         # JavaScript
├── README.md
└── .gitignore  
```

## Installation & Setup

### Step 1: Install Flask

```bash
pip install flask
```

### Step 2: Download/Clone the Project

```bash
git clone <your-repo-url>
cd task-manager
```

Or create the folder structure manually:
```bash
mkdir task-manager
cd task-manager
mkdir templates static
```

## How to Run

1. **Open terminal in project folder**

2. **Run the application**
   ```bash
   python3 app.py
   ```

3. **Open your browser and go to**
   ```
   http://127.0.0.1:5000
   ```

4. **Stop the server**
   - Press `Ctrl + C` in terminal

## How to Use

1. **Add Task**: Enter title and description, click "Add Task"
2. **Complete Task**: Click the "Complete" button (or "Incomplete" to undo)
3. **Delete Task**: Click "Delete" button and confirm
