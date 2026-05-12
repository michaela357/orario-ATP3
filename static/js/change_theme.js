const toggleSwitch = document.getElementById('toggleCheckbox');
const body = document.body;
const word = document.getElementById("light-dark-indicator")


function toggleDarkMode() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', targetTheme);
    
    localStorage.setItem('theme', targetTheme);
}

function sendAlert() {
    body.classList.toggle('dark-mode', toggleSwitch.checked)
    toggleDarkMode()
    if (toggleSwitch.checked) {
        console.log('light mode enabled!');
        word.textContent = "Enable Dark Mode!";
    } else {
        console.log('dark mode enabled!');
        word.textContent = "Enable Light Mode!";
}}

// On page load, check if they liked dark mode before
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
}

toggleSwitch.addEventListener('change', sendAlert);