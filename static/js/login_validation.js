document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const response = await fetch('/login', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.error) {
        const errorBox = document.getElementById('error-message')
        errorBox.innerText = result.error;
        errorBox.style.display = 'block';
        errorBox.style.opacity = '100';
        setTimeout(() => {
            errorBox.style.opacity = '0';
            setTimeout(() => { errorBox.style.display = 'none'; }, 500);
        }, 10000);
    } else {
        window.location.href = '/dashboard'; // Only reload if successful
    }
});