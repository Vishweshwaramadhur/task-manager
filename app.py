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

CATEGORY_TEMPLATES = {
    "Study": [
        ("Complete {} assignment", "Finish all exercises for {} before the deadline"),
        ("Read {} textbook", "Read chapters on {} for the upcoming exam"),
        ("Prepare {} presentation", "Create slides and notes for {} project"),
        ("Revise {} notes", "Go through all {} notes and make summaries"),
        ("Submit {} homework", "Complete and submit the {} homework on time"),
        ("Practice {} problems", "Solve at least 10 practice problems in {}"),
    ],
    "Shopping": [
        ("Buy {} from store", "Pick up {} along with other essentials"),
        ("Order {} online", "Check reviews and order {} from the best seller"),
        ("Get {} for kitchen", "Need to restock {} for the week"),
        ("Shop for {} clothes", "Find good deals on {} at the mall"),
        ("Purchase {} supplies", "Buy {} supplies before they run out"),
        ("Compare prices for {}", "Check multiple stores for the best price on {}"),
    ],
    "Business": [
        ("Prepare {} report", "Draft and review the {} report for management"),
        ("Schedule {} meeting", "Set up a meeting to discuss {} with the team"),
        ("Send {} proposal", "Finalize and send the {} proposal to the client"),
        ("Review {} contract", "Go through the {} contract terms carefully"),
        ("Update {} strategy", "Revise the {} strategy based on recent data"),
        ("Follow up on {} deal", "Check status and follow up on the {} deal"),
    ],
    "Personal": [
        ("Organize {}", "Sort and organize {} at home this weekend"),
        ("Call {} friend", "Catch up with {} over a phone call"),
        ("Fix {} at home", "Repair or replace the broken {} at home"),
        ("Clean {}", "Deep clean the {} area thoroughly"),
        ("Plan {} event", "Make arrangements for the upcoming {} event"),
        ("Update {} documents", "Renew or update all {} related documents"),
    ],
    "Health": [
        ("Do {} workout", "Complete a full {} workout session today"),
        ("Book {} appointment", "Schedule a {} checkup with the doctor"),
        ("Prepare {} meal", "Cook a healthy {} meal for the day"),
        ("Track {} intake", "Log daily {} intake in the health app"),
        ("Buy {} supplements", "Purchase {} supplements from the pharmacy"),
        ("Try {} exercise", "Start a new {} exercise routine this week"),
    ],
    "Finance": [
        ("Pay {} bill", "Clear the pending {} bill before due date"),
        ("Review {} expenses", "Analyze last month's {} spending"),
        ("Set up {} budget", "Create a monthly budget for {} expenses"),
        ("Compare {} plans", "Research and compare different {} plans"),
        ("File {} paperwork", "Complete and submit {} financial paperwork"),
        ("Cancel unused {} subscription", "Stop paying for the unused {} service"),
    ],
    "Travel": [
        ("Book {} tickets", "Search and book the best {} tickets available"),
        ("Pack {} essentials", "Prepare and pack all {} essentials for the trip"),
        ("Reserve {} accommodation", "Find and book {} accommodation online"),
        ("Plan {} itinerary", "Create a detailed {} travel itinerary"),
        ("Get {} insurance", "Purchase {} travel insurance before the trip"),
        ("Download {} maps", "Save offline {} maps for navigation"),
    ],
    "Other": [
        ("Donate old {}", "Gather and donate old {} to charity"),
        ("Return {} to store", "Take back the {} and get a refund"),
        ("Register for {} course", "Sign up for an online {} course"),
        ("Replace {} at home", "Buy a new {} to replace the old one"),
        ("Organize {} files", "Sort through and organize all {} files"),
        ("Learn about {}", "Spend time researching and learning about {}"),
    ],
}


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
    import random
    from faker import Faker
    fake = Faker()

    tasks = []
    for category in CATEGORIES:
        templates = CATEGORY_TEMPLATES[category]
        chosen = random.sample(templates, 3)
        for title_tpl, desc_tpl in chosen:
            word = fake.word().capitalize()
            title = title_tpl.format(word)
            description = desc_tpl.format(word)
            completed = random.choice([True, False])
            tasks.append((title, description, category, completed))

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO tasks (title, description, category, completed) VALUES (%s, %s, %s, %s)",
        tasks,
    )
    conn.commit()
    print(f"{len(tasks)} dummy tasks added across all categories.")
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
