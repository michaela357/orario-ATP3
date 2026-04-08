async function postForm(url, form) {
    const formData = new FormData(form);
    const csrfToken = formData.get('csrf_token');

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    });

    let result;

    try {
        result = await response.json();
    } catch {
        return {
            success: false,
            error: "CSRF Error, please refresh the page to logout"
        };
    }

    if (!result.success && result.redirect) {
        window.location.href = result.redirect;
        return result;
    }

    return result;
}

function showError(message) {
    const errorBox = document.getElementById('error-message');
    if (!errorBox) return;

    errorBox.innerText = message;
    errorBox.style.display = 'block';
    setTimeout(() => {
        errorBox.style.opacity = '0';
        setTimeout(() => { errorBox.style.display = 'none'; }, 500);
    }, 6000);
}

function showSuccess(message) {
    const successBox = document.getElementById('success-message');
    if (!successBox) return;

    successBox.innerText = message;
    successBox.style.display = 'block';
    setTimeout(() => {
        successBox.style.opacity = '0';
        setTimeout(() => { successBox.style.display = 'none'; }, 500);
    }, 6000);
}