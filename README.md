# Task Manager

A simple task manager web app built with Flask and MySQL that lets you create, complete, and delete tasks with a clean Bootstrap UI.

## Features

- Add new tasks with title and description
- Edit tasks inline (both pending and completed tasks)
- Mark tasks as complete (moves them off the main page)
- Delete tasks (both pending and completed)
- View completed tasks in a separate modal
- Main page shows only pending tasks
- Task timestamps (created at)
- Input validation (length limits, required fields)
- Responsive design with Bootstrap 5
- Error handling

## Tech Stack

- **Backend:** Flask, MySQL Connector, python-dotenv
- **Frontend:** HTML5, Bootstrap 5, Bootstrap Icons, JavaScript
- **Database:** MySQL

## Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd task-manager
```

2. Create `.env` file from sample
```bash
cp .env.sample .env
```

3. Update `.env` with your MySQL credentials
```
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=taskmanager
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Run the application
```bash
python app.py
```

6. Open browser at `http://127.0.0.1:5000`

> The tasks table is created automatically on first run.

## Project Structure

```
task-manager/
├── app.py
├── requirements.txt
├── .env
├── .env.sample
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── README.md
```

## Environment Variables

Create a `.env` file with the following variables:

```
FLASK_DEBUG=True

DB_HOST=localhost
DB_USER=your_user_here
DB_PASSWORD=your_password_here
DB_NAME=taskmanager
```

## License

Free to use for learning and portfolio projects.
