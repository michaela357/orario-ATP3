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