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

// Clear all pending tasks (optionally by category)
async function clearAllPending(category) {
    var msg = category
        ? `Delete all pending "${category}" tasks? This cannot be undone.`
        : "Delete all pending tasks? This cannot be undone.";
    if (confirm(msg)) {
        try {
            var url = "/delete-pending";
            if (category) url += "?category=" + encodeURIComponent(category);
            await fetch(url, { method: "DELETE" });
            location.reload();
        } catch (error) {
            alert("Error clearing pending tasks: " + error);
        }
    }
}

// Clear all completed tasks (optionally by category)
async function clearAllCompleted(category) {
    var msg = category
        ? `Delete all completed "${category}" tasks? This cannot be undone.`
        : "Delete all completed tasks? This cannot be undone.";
    if (confirm(msg)) {
        try {
            var url = "/delete-completed";
            if (category) url += "?category=" + encodeURIComponent(category);
            await fetch(url, { method: "DELETE" });
            location.reload();
        } catch (error) {
            alert("Error clearing completed tasks: " + error);
        }
    }
}
