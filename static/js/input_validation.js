const passwordInput = document.getElementById('password');

const requirements = {
    length: { re: /.{8,64}/, element: document.getElementById('length') },
    uppercase: { re: /[A-Z]/, element: document.getElementById('uppercase') },
    number: { re: /[0-9]/, element: document.getElementById('number') },
    special: { re: /[!@#$%^&*]/, element: document.getElementById('special') }
};

    
function updateRequirements() {
    const value = passwordInput.value;

    for (const key in requirements) {
        const item = requirements[key];
        if (item.re.test(value)) {
            item.element.style.color = 'green';
            item.element.innerHTML = `✔ ${item.element.innerText.slice(2)}`;
        } else {
            item.element.style.color = 'red';
            item.element.innerHTML = `✖ ${item.element.innerText.slice(2)}`;
        }
    }
    if (Object.values(requirements).every(item => item.re.test(value))) {
        const successBox = document.getElementById('success-message')
        successBox.innerText = 'Valid password!';
        successBox.style.display = 'block';
        successBox.style.opacity = '100';
        setTimeout(() => {
            successBox.style.opacity = '0';
            setTimeout(() => { successBox.style.display = 'none'; }, 3000);
        }, 10000);

    }
};

document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const response = await fetch('/register', {
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


passwordInput.addEventListener('input', updateRequirements)