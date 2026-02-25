# Task Manager

> A multi-page task management web application built with Flask and MySQL, featuring category-based organization, PDF export, sorting, filtering, and a responsive Bootstrap 5 UI.

---

## Features

- **Category-based organization** — 8 predefined categories: Study, Shopping, Business, Personal, Health, Finance, Travel, Other
- **Category detail pages** — view pending and completed tasks per category with counts
- **Add / Edit tasks** — title, description, and category fields with input validation
- **Complete & Undo** — mark tasks as complete or move them back to pending
- **Sort** — by Newest, Oldest, A–Z, Z–A
- **Filter** — by category on pending and completed pages
- **Bulk delete** — clear all pending or completed tasks per page or per category
- **PDF export** — download tasks as PDF (all, pending, completed, or per category)
- **Seed dummy data** — generate 24 random tasks via CLI using Faker (3 per category)
- **Flash messages** — success and error feedback on all actions
- **Responsive design** — Bootstrap 5 with Bootstrap Icons

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, Flask, MySQL Connector, python-dotenv, fpdf2, Faker |
| Frontend | HTML5, Bootstrap 5, Bootstrap Icons, JavaScript |
| Database | MySQL |

---

## Prerequisites

- Python 3.8+
- MySQL server running locally
- `pip` package manager

---

## Getting Started

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd task-manager
```

**2. Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.sample .env
```

Edit `.env` with your MySQL credentials:

```env
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

DB_HOST=localhost
DB_USER=your_user_here
DB_PASSWORD=your_password_here
DB_NAME=taskmanager
```

**5. Run the application**

```bash
python app.py
```

**6. Open in browser**

```
http://127.0.0.1:5000
```

> The `tasks` table is created automatically on first run.

---

## Usage

### Seed Dummy Data

Generate 24 sample tasks (3 per category) for testing:

```bash
python app.py seed
```

This command can be run multiple times to append more dummy data.


---

## License

This project is free to use for learning and portfolio purposes.
