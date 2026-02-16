// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Add a new task
async function addTask() {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();

    if (title === "" || description === "") {
        alert("Title and Description cannot be empty!");
        return;
    }

    try {
        const response = await fetch("/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description }),
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

// Toggle task completion
async function toggleTask(id) {
    try {
        await fetch(`/toggle/${id}`, { method: "PATCH" });
        location.reload();
    } catch (error) {
        alert("Error updating task: " + error);
    }
}

// Delete task
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

// Enter edit mode for a task
function editTask(id) {
    document.getElementById(`display-${id}`).classList.add("d-none");
    document.getElementById(`edit-${id}`).classList.remove("d-none");
    document.getElementById(`edit-btn-${id}`).classList.add("d-none");
    document.getElementById(`save-btn-${id}`).classList.remove("d-none");
    document.getElementById(`cancel-btn-${id}`).classList.remove("d-none");
    document.getElementById(`edit-title-${id}`).focus();
}

// Cancel edit mode
function cancelEdit(id) {
    document.getElementById(`display-${id}`).classList.remove("d-none");
    document.getElementById(`edit-${id}`).classList.add("d-none");
    document.getElementById(`edit-btn-${id}`).classList.remove("d-none");
    document.getElementById(`save-btn-${id}`).classList.add("d-none");
    document.getElementById(`cancel-btn-${id}`).classList.add("d-none");
}

// Save edited task
async function saveTask(id) {
    const title = document.getElementById(`edit-title-${id}`).value.trim();
    const description = document.getElementById(`edit-desc-${id}`).value.trim();

    if (title === "" || description === "") {
        alert("Title and Description cannot be empty!");
        return;
    }

    try {
        const response = await fetch(`/edit/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description }),
        });

        const result = await response.json();

        if (response.ok) {
            location.reload();
        } else {
            alert(result.error || result.message);
        }
    } catch (error) {
        alert("Error saving task: " + error);
    }
}

// Enter edit mode for a completed task in modal
function editCompletedTask(id) {
    document.getElementById(`completed-title-${id}`).classList.add("d-none");
    document.getElementById(`completed-desc-${id}`).classList.add("d-none");
    document.getElementById(`completed-edit-title-${id}`).classList.remove("d-none");
    document.getElementById(`completed-edit-desc-${id}`).classList.remove("d-none");
    document.getElementById(`completed-edit-btn-${id}`).classList.add("d-none");
    document.getElementById(`completed-save-btn-${id}`).classList.remove("d-none");
    document.getElementById(`completed-cancel-btn-${id}`).classList.remove("d-none");
    document.getElementById(`completed-edit-title-${id}`).focus();
}

// Cancel edit mode for a completed task
function cancelCompletedEdit(id) {
    document.getElementById(`completed-title-${id}`).classList.remove("d-none");
    document.getElementById(`completed-desc-${id}`).classList.remove("d-none");
    document.getElementById(`completed-edit-title-${id}`).classList.add("d-none");
    document.getElementById(`completed-edit-desc-${id}`).classList.add("d-none");
    document.getElementById(`completed-edit-btn-${id}`).classList.remove("d-none");
    document.getElementById(`completed-save-btn-${id}`).classList.add("d-none");
    document.getElementById(`completed-cancel-btn-${id}`).classList.add("d-none");
}

// Save edited completed task
async function saveCompletedTask(id) {
    const title = document.getElementById(`completed-edit-title-${id}`).value.trim();
    const description = document.getElementById(`completed-edit-desc-${id}`).value.trim();

    if (title === "" || description === "") {
        alert("Title and Description cannot be empty!");
        return;
    }

    try {
        const response = await fetch(`/edit/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description }),
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById(`completed-title-${id}`).textContent = title;
            document.getElementById(`completed-desc-${id}`).textContent = description;
            document.getElementById(`completed-edit-title-${id}`).value = title;
            document.getElementById(`completed-edit-desc-${id}`).value = description;
            cancelCompletedEdit(id);
        } else {
            alert(result.error || result.message);
        }
    } catch (error) {
        alert("Error saving task: " + error);
    }
}

// Delete a completed task from modal
async function deleteCompletedTask(id) {
    if (confirm("Delete this task?")) {
        try {
            const response = await fetch(`/delete/${id}`, { method: "DELETE" });
            if (response.ok) {
                document.getElementById(`completed-row-${id}`).remove();
                const tbody = document.getElementById("done-tbody");
                if (tbody.children.length === 0) {
                    document.getElementById("done-table").classList.add("d-none");
                    document.getElementById("no-done-msg").classList.remove("d-none");
                } else {
                    Array.from(tbody.children).forEach((row, i) => {
                        row.cells[0].textContent = i + 1;
                    });
                }
            } else {
                const result = await response.json();
                alert(result.error || "Error deleting task");
            }
        } catch (error) {
            alert("Error deleting task: " + error);
        }
    }
}

// Show completed tasks in modal
async function showCompleted() {
    try {
        const response = await fetch("/completed");
        const tasks = await response.json();
        const tbody = document.getElementById("done-tbody");
        const noMsg = document.getElementById("no-done-msg");
        const table = document.getElementById("done-table");

        tbody.innerHTML = "";

        if (tasks.length === 0) {
            table.classList.add("d-none");
            noMsg.classList.remove("d-none");
        } else {
            table.classList.remove("d-none");
            noMsg.classList.add("d-none");

            tasks.forEach((task, index) => {
                const row = document.createElement("tr");
                row.id = `completed-row-${task.id}`;

                const cellIndex = document.createElement("td");
                cellIndex.textContent = index + 1;
                row.appendChild(cellIndex);

                const cellTitle = document.createElement("td");
                cellTitle.innerHTML = `<span id="completed-title-${task.id}">${escapeHtml(task.title)}</span>` +
                    `<input type="text" class="form-control form-control-sm d-none" id="completed-edit-title-${task.id}" value="${escapeHtml(task.title)}">`;
                row.appendChild(cellTitle);

                const cellDesc = document.createElement("td");
                cellDesc.innerHTML = `<span id="completed-desc-${task.id}">${escapeHtml(task.description)}</span>` +
                    `<input type="text" class="form-control form-control-sm d-none" id="completed-edit-desc-${task.id}" value="${escapeHtml(task.description)}">`;
                row.appendChild(cellDesc);

                const cellDate = document.createElement("td");
                cellDate.textContent = task.created_at || "\u2014";
                row.appendChild(cellDate);

                const cellActions = document.createElement("td");
                cellActions.innerHTML = `<button class="btn btn-sm btn-outline-secondary me-1" id="completed-edit-btn-${task.id}" onclick="editCompletedTask(${task.id})"><i class="bi bi-pencil"></i></button>` +
                    `<button class="btn btn-sm btn-outline-danger" id="completed-delete-btn-${task.id}" onclick="deleteCompletedTask(${task.id})"><i class="bi bi-trash"></i></button>` +
                    `<button class="btn btn-sm btn-outline-success d-none me-1" id="completed-save-btn-${task.id}" onclick="saveCompletedTask(${task.id})"><i class="bi bi-check-lg"></i></button>` +
                    `<button class="btn btn-sm btn-outline-warning d-none" id="completed-cancel-btn-${task.id}" onclick="cancelCompletedEdit(${task.id})"><i class="bi bi-x-lg"></i></button>`;
                row.appendChild(cellActions);

                tbody.appendChild(row);
            });
        }

        const modal = new bootstrap.Modal(document.getElementById("doneModal"));
        modal.show();
    } catch (error) {
        alert("Error fetching completed tasks: " + error);
    }
}
