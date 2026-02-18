# Task Manager

A simple task manager web app built with Flask and MySQL with a clean multi-page Bootstrap UI.

## Features

- **Dashboard** with pending and completed task counts
- **Add tasks** with title and description on a dedicated page
- **Edit tasks** on a separate edit page with save and cancel
- **Mark tasks as complete** from the pending tasks page
- **Delete tasks** (both pending and completed)
- **View completed tasks** on a full-page table
- Template inheritance with a shared navbar
- Input validation (length limits, required fields)
- Flash messages for success/error feedback
- Responsive design with Bootstrap 5

## Pages

| URL | Page | Description |
|-----|------|-------------|
| `/` | Dashboard | Task counts + links to all pages |
| `/add-task` | Add Task | Form to create a new task |
| `/tasks` | Pending Tasks | List with complete/edit/delete actions |
| `/completed` | Completed Tasks | Table with edit/delete actions |
| `/edit/<id>` | Edit Task | Form to edit title and description |

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
│   ├── base.html
│   ├── index.html
│   ├── add_task.html
│   ├── tasks.html
│   ├── completed.html
│   └── edit_task.html
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
SECRET_KEY=your_secret_key_here

DB_HOST=localhost
DB_USER=your_user_here
DB_PASSWORD=your_password_here
DB_NAME=taskmanager
```

## License

Free to use for learning and portfolio projects.
