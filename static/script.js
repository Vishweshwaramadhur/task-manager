// Add a new task
async function addTask() {
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();

    if (title === "" || description === "") {
        alert("Title and Description cannot be empty!");
        return;
    }

    try {
        const response = await fetch('/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description })
        });

        const result = await response.json();

        if (response.ok) {
            location.reload();
        } else {
            alert(result.error || result.message);
        }
    } catch (error) {
        alert("Error adding task: " + error);
    }
}

// Toggle task completion (USE ID, NOT INDEX)
async function toggleTask(id) {
    try {
        await fetch(`/toggle/${id}`, { method: 'POST' });
        location.reload();
    } catch (error) {
        alert("Error updating task: " + error);
    }
}

// Delete task (USE ID, NOT INDEX)
async function deleteTask(id) {
    if (confirm("Delete this task?")) {
        try {
            await fetch(`/delete/${id}`, { method: 'POST' });
            location.reload();
        } catch (error) {
            alert("Error deleting task: " + error);
        }
    }
}
