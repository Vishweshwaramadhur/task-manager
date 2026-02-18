# Task Manager

A multi-page task manager web app built with Flask and MySQL with a clean Bootstrap UI. Organize tasks by categories with sorting, filtering, PDF export, and more.

## Features

- **Category-based organization** — 8 predefined categories: Study, Shopping, Business, Personal, Health, Finance, Travel, Other
- **Category detail pages** — view pending and completed tasks per category with counts
- **Add tasks** with title, description, and required category
- **Edit tasks** with category preserved
- **Mark tasks as complete** and **undo complete** to move back to pending
- **Sort tasks** by Newest, Oldest, A-Z, Z-A
- **Filter tasks** by category on pending and completed pages
- **Clear all pending** — bulk delete all pending tasks (per page or per category)
- **Clear all completed** — bulk delete all completed tasks (per page or per category)
- **Export as PDF** — download tasks as PDF (all, pending, completed, or per category)
- **Seed dummy data** — terminal command to generate 24 unique random tasks using Faker (3 per category)
- **Back to Home** navigation on every page
- Input validation (length limits, required fields)
- Flash messages for success/error feedback
- Responsive design with Bootstrap 5

## Pages

| URL | Page | Description |
|-----|------|-------------|
| `/` | Home | Category cards with task counts + Add New Task |
| `/category/<name>` | Category Detail | Pending & completed tasks, stats, add/export/clear actions |
| `/add-task` | Add Task | Form with title, description, category (required) |
| `/edit/<id>` | Edit Task | Form to edit title, description, and category |
| `/tasks` | Pending Tasks | Full list with sort, filter, complete/edit/delete actions |
| `/completed` | Completed Tasks | Table with sort, filter, undo/edit/delete actions |
| `/export/pdf` | Export PDF | Download tasks as PDF (`?type=pending\|completed\|all&category=`) |

## Tech Stack

- **Backend:** Flask, MySQL Connector, python-dotenv, fpdf2, Faker
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

## Seed Dummy Data

To add 24 sample tasks (3 per category) for testing, run:

```bash
python app.py seed
```

You can run this command multiple times to add more dummy data.

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
│   ├── category.html
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
