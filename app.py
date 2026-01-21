from flask import Flask, render_template, request, jsonify
import mysql.connector

# Create Flask app
app = Flask(__name__)

# -------------------------------
# MySQL Database Connection
# -------------------------------
db = mysql.connector.connect(
    host="localhost",
    user="flaskuser",          # NEW user
    password="Flask@1234",     # Strong password
    database="taskmanager"
)

cursor = db.cursor(dictionary=True)

# -------------------------------
# HOME - List all tasks
# -------------------------------
@app.route('/')
def home():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    return render_template("index.html", tasks=tasks)

# -------------------------------
# ADD TASK
# -------------------------------
@app.route('/add', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title or not description:
        return jsonify({'error': 'Title and description required'}), 400

    query = "INSERT INTO tasks (title, description) VALUES (%s, %s)"
    cursor.execute(query, (title, description))
    db.commit()

    return jsonify({'message': 'Task added successfully'}), 201

# -------------------------------
# TOGGLE TASK (Complete / Incomplete)
# -------------------------------
@app.route('/toggle/<int:id>', methods=['POST'])
def toggle_task(id):
    cursor.execute("SELECT completed FROM tasks WHERE id=%s", (id,))
    task = cursor.fetchone()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    new_status = not task['completed']
    cursor.execute(
        "UPDATE tasks SET completed=%s WHERE id=%s",
        (new_status, id)
    )
    db.commit()

    return jsonify({'message': 'Task updated successfully'}), 200

# -------------------------------
# DELETE TASK
# -------------------------------
@app.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
    db.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
