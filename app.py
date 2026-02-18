from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "taskmanager"),
}


def get_db():
    """Get a database connection for the current request."""
    if "db" not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close the database connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tasks table if it doesn't exist."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    cursor.close()
    conn.close()


# ── Page Routes ──────────────────────────────────────────────

@app.route("/")
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS cnt FROM tasks WHERE completed=0")
    pending_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) AS cnt FROM tasks WHERE completed=1")
    completed_count = cursor.fetchone()["cnt"]
    cursor.close()
    return render_template(
        "index.html",
        pending_count=pending_count,
        completed_count=completed_count,
        active_page="home",
    )


@app.route("/add-task")
def add_task_page():
    return render_template("add_task.html", active_page="add_task")


@app.route("/tasks")
def tasks_page():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE completed=0 ORDER BY id DESC")
    tasks = cursor.fetchall()
    cursor.close()
    return render_template("tasks.html", tasks=tasks, active_page="tasks")


@app.route("/completed")
def completed_page():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE completed=1 ORDER BY id DESC")
    tasks = cursor.fetchall()
    cursor.close()

    for task in tasks:
        if task.get("created_at"):
            task["created_at"] = task["created_at"].strftime("%Y-%m-%d %H:%M")

    return render_template("completed.html", tasks=tasks, active_page="completed")


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
    # Support both JSON API and HTML form submissions
    if request.is_json:
        data = request.get_json()
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
    else:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

    if not title or not description:
        if request.is_json:
            return jsonify({"error": "Title and description required"}), 400
        flash("Title and description are required.", "danger")
        return redirect(url_for("add_task_page"))

    if len(title) > 255 or len(description) > 2000:
        if request.is_json:
            return jsonify({"error": "Title (max 255) or description (max 2000) too long"}), 400
        flash("Title (max 255) or description (max 2000) too long.", "danger")
        return redirect(url_for("add_task_page"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        (title, description),
    )
    db.commit()
    cursor.close()

    if request.is_json:
        return jsonify({"message": "Task added successfully"}), 201

    flash("Task added successfully!", "success")
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

    # GET - show edit form
    if request.method == "GET":
        back_url = url_for("completed_page") if task["completed"] else url_for("tasks_page")
        return render_template("edit_task.html", task=task, back_url=back_url)

    # POST (form) or PUT (JSON API)
    if request.is_json:
        data = request.get_json()
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
    else:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

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
        "UPDATE tasks SET title=%s, description=%s WHERE id=%s",
        (title, description, task_id),
    )
    db.commit()
    cursor.close()

    if request.is_json:
        return jsonify({"message": "Task updated successfully"}), 200

    flash("Task updated successfully!", "success")
    redirect_url = url_for("completed_page") if task["completed"] else url_for("tasks_page")
    return redirect(redirect_url)


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1"))
