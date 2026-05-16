// Open popup
function addTaskPopup() {
    document.getElementById("popupOverlay").style.display = "block";
}

// Close popup
function closeAddPopup() {
    document.getElementById("popupOverlay").style.display = "none";
}

// Simple form validation
function validateForm(event) {
    event.preventDefault(); // Important: Stop the page from refreshing immediately

    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const due_date = document.getElementById("due_date").value.trim();
    const reminder = document.getElementById("reminder").checked; // Get boolean value
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    if (!title || !description || !due_date) {
        alert("Please fill in all fields.");
        return false;
    }

    fetch('/api/add_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            title: title, 
            description: description, 
            due_date: due_date, 
            reminder: reminder 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeAddPopup();
            location.reload();
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Close popup when clicking outside the form
window.onclick = function(event) {
    const overlay = document.getElementById("popupOverlay");
    if (event.target === overlay) {
        closeAddPopup();
    }
}

async function toggleComplete(taskId, currentStatus) {

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const response = await fetch(`/api/edit_task/${taskId}`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                is_complete: !currentStatus
            })
        }
    );

    const data = await response.json();
    if (data.success) {
        location.reload();
    } else {
        alert(data.error);
    }
}

// Delete Task
async function deleteTask(taskId) {
    if (!confirm("Delete this task?")) {
        return;
    }
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const response = await fetch(
        `/api/delete_task/${taskId}`,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        }
    );
    const data = await response.json();
    if (data.success) {
        location.reload();
    } else {
        alert(data.error);
    }
}

function openEditPopup(taskId, title, description, dueDate, reminder, isComplete) {

    document.getElementById("edit-task-id").value = taskId;
    document.getElementById("edit-title").value = title;
    document.getElementById("edit-description").value = description;
    document.getElementById("edit-due-date").value = dueDate;
    document.getElementById("edit-reminder").checked = reminder;
    document.getElementById("edit-is-complete").checked = isComplete;
    document.getElementById("editPopupOverlay").style.display = "block";
}

function closeEditPopup() {
    document.getElementById("editPopupOverlay").style.display = "none";
}

document.getElementById("edit-task-form")
?.addEventListener("submit", async function(e) {

    e.preventDefault();

    const taskId =
        document.getElementById("edit-task-id").value;

    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        .getAttribute("content");

    const response = await fetch(
        `/api/edit_task/${taskId}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },

            body: JSON.stringify({
                title: document.getElementById("edit-title").value,
                description: document.getElementById("edit-description").value,
                due_date: document.getElementById("edit-due-date").value,
                reminder: document.getElementById("edit-reminder").checked,
                is_complete: document.getElementById("edit-is-complete").checked
            })
        }
    );

    const data = await response.json();

    if (data.success) {
        closeEditPopup();
        location.reload();
    } else {
        alert(data.error);
    }
});