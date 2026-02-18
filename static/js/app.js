// Toggle task completion
async function toggleTask(id) {
    try {
        await fetch(`/toggle/${id}`, { method: "PATCH" });
        location.reload();
    } catch (error) {
        alert("Error updating task: " + error);
    }
}

// Delete task (pending)
async function deleteTask(id) {
    if (confirm("Delete this task?")) {
        try {
            await fetch(`/delete/${id}`, { method: "DELETE" });
            location.reload();
        } catch (error) {
            alert("Error deleting task: " + error);
        }
    }
}

// Delete task (completed)
async function deleteCompletedTask(id) {
    if (confirm("Delete this task?")) {
        try {
            await fetch(`/delete/${id}`, { method: "DELETE" });
            location.reload();
        } catch (error) {
            alert("Error deleting task: " + error);
        }
    }
}
