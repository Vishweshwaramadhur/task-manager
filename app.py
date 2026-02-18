import sys

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g, Response
from fpdf import FPDF
import mysql.connector
import os
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "taskmanager"),
}

SORT_OPTIONS = {
    "newest": "id DESC",
    "oldest": "id ASC",
    "az": "title ASC",
    "za": "title DESC",
}

CATEGORIES = ["Study", "Shopping", "Business", "Personal", "Health", "Finance", "Travel", "Other"]

DUMMY_TASKS = [
    ("Complete Math Assignment", "Finish chapters 5 and 6 exercises", "Study", False),
    ("Read Science Textbook", "Read pages 100-150 for upcoming test", "Study", False),
    ("Prepare Presentation", "Create slides for history project", "Study", True),
    ("Buy Groceries", "Milk, eggs, bread, vegetables, fruits", "Shopping", False),
    ("Order New Headphones", "Check reviews and order from Amazon", "Shopping", False),
    ("Buy Birthday Gift", "Get a gift for friend's birthday party", "Shopping", True),
    ("Client Meeting Prep", "Prepare agenda and slides for Monday meeting", "Business", False),
    ("Send Invoice", "Send pending invoices to 3 clients", "Business", False),
    ("Update Business Plan", "Revise Q2 targets and budget", "Business", True),
    ("Clean Room", "Organize desk and wardrobe", "Personal", False),
    ("Call Parents", "Weekly catch-up call with family", "Personal", False),
    ("Renew Passport", "Submit renewal application online", "Personal", True),
    ("Morning Workout", "30 min jogging + stretching routine", "Health", False),
    ("Book Doctor Appointment", "Annual health checkup with Dr. Sharma", "Health", False),
    ("Meal Prep Sunday", "Prepare healthy meals for the week", "Health", True),
    ("Pay Electricity Bill", "Due date is end of this month", "Finance", False),
    ("Review Monthly Budget", "Track expenses and savings for this month", "Finance", False),
    ("File Tax Returns", "Gather documents and submit returns", "Finance", True),
    ("Book Flight Tickets", "Check prices for Goa trip next month", "Travel", False),
    ("Pack Travel Bag", "Prepare checklist and pack essentials", "Travel", False),
    ("Hotel Reservation", "Book hotel for weekend getaway", "Travel", True),
    ("Fix Leaking Tap", "Call plumber or fix it yourself", "Other", False),
    ("Update Resume", "Add recent projects and skills", "Other", False),
    ("Return Library Books", "3 books due this Friday", "Other", True),
]


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category VARCHAR(100) DEFAULT NULL
        )"""
    )
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN category VARCHAR(100) DEFAULT NULL")
    except mysql.connector.errors.ProgrammingError:
        pass
    conn.commit()
    cursor.close()
    conn.close()


def seed_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO tasks (title, description, category, completed) VALUES (%s, %s, %s, %s)",
        DUMMY_TASKS,
    )
    conn.commit()
    print(f"{len(DUMMY_TASKS)} dummy tasks added across all categories.")
    cursor.close()
    conn.close()


# ── Page Routes ──────────────────────────────────────────────

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """SELECT category, COUNT(*) AS cnt
           FROM tasks
           WHERE category IS NOT NULL AND category != ''
           GROUP BY category"""
    )
    cat_counts = {row["category"]: row["cnt"] for row in cursor.fetchall()}
    cursor.close()
    return render_template("index.html", categories=CATEGORIES, cat_counts=cat_counts, active_page="home")


@app.route("/category/<category_name>")
def category_page(category_name):
    if category_name not in CATEGORIES:
        flash("Category not found.", "danger")
        return redirect(url_for("home"))

    sort = request.args.get("sort", "newest")
    order_by = SORT_OPTIONS.get(sort, "id DESC")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM tasks WHERE category=%s AND completed=0 ORDER BY {order_by}", (category_name,))
    pending_tasks = cursor.fetchall()

    cursor.execute(f"SELECT * FROM tasks WHERE category=%s AND completed=1 ORDER BY {order_by}", (category_name,))
    completed_tasks = cursor.fetchall()

    for task in completed_tasks:
        if task.get("created_at"):
            task["created_at"] = task["created_at"].strftime("%Y-%m-%d %H:%M")

    cursor.close()
    return render_template(
        "category.html",
        category_name=category_name,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        pending_count=len(pending_tasks),
        completed_count=len(completed_tasks),
        total_count=len(pending_tasks) + len(completed_tasks),
        current_sort=sort,
    )


@app.route("/add-task")
def add_task_page():
    selected_category = request.args.get("category", "")
    return render_template("add_task.html", active_page="add_task", categories=CATEGORIES, selected_category=selected_category)


@app.route("/tasks")
def tasks_page():
    sort = request.args.get("sort", "newest")
    category = request.args.get("category", "")
    order_by = SORT_OPTIONS.get(sort, "id DESC")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM tasks WHERE completed=0"
    params = []
    if category:
        query += " AND category=%s"
        params.append(category)
    query += f" ORDER BY {order_by}"

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    cursor.close()
    return render_template(
        "tasks.html",
        tasks=tasks,
        active_page="tasks",
        current_sort=sort,
        current_category=category,
        categories=CATEGORIES,
    )


@app.route("/completed")
def completed_page():
    sort = request.args.get("sort", "newest")
    category = request.args.get("category", "")
    order_by = SORT_OPTIONS.get(sort, "id DESC")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM tasks WHERE completed=1"
    params = []
    if category:
        query += " AND category=%s"
        params.append(category)
    query += f" ORDER BY {order_by}"

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    cursor.close()

    for task in tasks:
        if task.get("created_at"):
            task["created_at"] = task["created_at"].strftime("%Y-%m-%d %H:%M")

    return render_template(
        "completed.html",
        tasks=tasks,
        active_page="completed",
        current_sort=sort,
        current_category=category,
        categories=CATEGORIES,
    )


# ── API Routes ───────────────────────────────────────────────

@app.route("/api/completed")
def api_completed_tasks():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE completed=1 ORDER BY id DESC")
    tasks = cursor.fetchall()
    cursor.close()

    for task in tasks:
        if task.get("created_at"):
            task["created_at"] = task["created_at"].strftime("%Y-%m-%d %H:%M")

    return jsonify(tasks), 200


@app.route("/add", methods=["POST"])
def add_task():
    if request.is_json:
        data = request.get_json()
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        category = data.get("category", "").strip()
    else:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

    if not title or not description or not category:
        if request.is_json:
            return jsonify({"error": "Title, description and category required"}), 400
        flash("Title, description and category are required.", "danger")
        return redirect(url_for("add_task_page"))

    if len(title) > 255 or len(description) > 2000:
        if request.is_json:
            return jsonify({"error": "Title (max 255) or description (max 2000) too long"}), 400
        flash("Title (max 255) or description (max 2000) too long.", "danger")
        return redirect(url_for("add_task_page"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, category) VALUES (%s, %s, %s)",
        (title, description, category or None),
    )
    db.commit()
    cursor.close()

    if request.is_json:
        return jsonify({"message": "Task added successfully"}), 201

    flash("Task added successfully!", "success")
    if category and category in CATEGORIES:
        return redirect(url_for("category_page", category_name=category))
    return redirect(url_for("tasks_page"))


@app.route("/toggle/<int:task_id>", methods=["PATCH"])
def toggle_task(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT completed FROM tasks WHERE id=%s", (task_id,))
    task = cursor.fetchone()

    if not task:
        cursor.close()
        return jsonify({"error": "Task not found"}), 404

    new_status = not task["completed"]
    cursor.execute("UPDATE tasks SET completed=%s WHERE id=%s", (new_status, task_id))
    db.commit()
    cursor.close()
    return jsonify({"message": "Task updated successfully"}), 200


@app.route("/delete/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id=%s", (task_id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Task not found"}), 404

    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.commit()
    cursor.close()
    return jsonify({"message": "Task deleted successfully"}), 200


@app.route("/delete-pending", methods=["DELETE"])
def delete_pending():
    category = request.args.get("category", "")
    db = get_db()
    cursor = db.cursor()
    if category:
        cursor.execute("DELETE FROM tasks WHERE completed=0 AND category=%s", (category,))
    else:
        cursor.execute("DELETE FROM tasks WHERE completed=0")
    deleted = cursor.rowcount
    db.commit()
    cursor.close()
    return jsonify({"message": f"{deleted} pending tasks deleted"}), 200


@app.route("/delete-completed", methods=["DELETE"])
def delete_completed():
    category = request.args.get("category", "")
    db = get_db()
    cursor = db.cursor()
    if category:
        cursor.execute("DELETE FROM tasks WHERE completed=1 AND category=%s", (category,))
    else:
        cursor.execute("DELETE FROM tasks WHERE completed=1")
    deleted = cursor.rowcount
    db.commit()
    cursor.close()
    return jsonify({"message": f"{deleted} completed tasks deleted"}), 200


@app.route("/edit/<int:task_id>", methods=["GET", "POST", "PUT"])
def edit_task(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
    task = cursor.fetchone()
    cursor.close()

    if not task:
        if request.method == "GET":
            flash("Task not found.", "danger")
            return redirect(url_for("tasks_page"))
        return jsonify({"error": "Task not found"}), 404

    if request.method == "GET":
        if task.get("category") and task["category"] in CATEGORIES:
            back_url = url_for("category_page", category_name=task["category"])
        elif task["completed"]:
            back_url = url_for("completed_page")
        else:
            back_url = url_for("tasks_page")
        return render_template("edit_task.html", task=task, back_url=back_url, categories=CATEGORIES)

    if request.is_json:
        data = request.get_json()
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        category = data.get("category", "").strip()
    else:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

    if not title or not description:
        if request.is_json:
            return jsonify({"error": "Title and description required"}), 400
        flash("Title and description are required.", "danger")
        return redirect(url_for("edit_task", task_id=task_id))

    if len(title) > 255 or len(description) > 2000:
        if request.is_json:
            return jsonify({"error": "Title (max 255) or description (max 2000) too long"}), 400
        flash("Title (max 255) or description (max 2000) too long.", "danger")
        return redirect(url_for("edit_task", task_id=task_id))

    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET title=%s, description=%s, category=%s WHERE id=%s",
        (title, description, category or None, task_id),
    )
    db.commit()
    cursor.close()

    if request.is_json:
        return jsonify({"message": "Task updated successfully"}), 200

    flash("Task updated successfully!", "success")
    cat = category or task.get("category")
    if cat and cat in CATEGORIES:
        return redirect(url_for("category_page", category_name=cat))
    redirect_url = url_for("completed_page") if task["completed"] else url_for("tasks_page")
    return redirect(redirect_url)


@app.route("/export/pdf")
def export_pdf():
    task_type = request.args.get("type", "all")
    category = request.args.get("category", "")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if task_type == "pending":
        query = "SELECT * FROM tasks WHERE completed=0"
        title = "Pending Tasks"
    elif task_type == "completed":
        query = "SELECT * FROM tasks WHERE completed=1"
        title = "Completed Tasks"
    else:
        query = "SELECT * FROM tasks WHERE 1=1"
        title = "All Tasks"

    params = []
    if category:
        query += " AND category=%s"
        params.append(category)
        title += f" - {category}"

    query += " ORDER BY completed ASC, id DESC"
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    if not tasks:
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "No tasks found.", new_x="LMARGIN", new_y="NEXT", align="C")
    else:
        for task in tasks:
            status = "Completed" if task["completed"] else "Pending"
            cat = task.get("category") or ""

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, f"{task['title']}  [{status}]", new_x="LMARGIN", new_y="NEXT")

            if cat:
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 6, f"Category: {cat}", new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, task.get("description") or "")
            pdf.ln(4)

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)

    return Response(
        buf.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={title.lower().replace(' ', '_')}.pdf"},
    )


if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed_db()
    else:
        app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1"))
