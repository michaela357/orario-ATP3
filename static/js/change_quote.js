const editButton = document.getElementById("name-edit");
const newQuote = document.getElementById('editable-quote');
const ENTER_KEY_CODE = 13;
const saveMsg = document.getElementById('save-msg');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function handleInputKey(event) {

    if (event.keyCode === ENTER_KEY_CODE) {

    event.preventDefault();
    n_quote = newQuote.textContent

    if (n_quote.length > 250 || n_quote.length === 0) {
        alert("Please enter a quote that is shorter than 250 characters.")
    } else {
        fetch('/api/update_quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ quote: n_quote })
        })
    
    
        newQuote.contentEditable = "false";
        newQuote.blur();
        editButton.setAttribute('hidden', 'true');
    
        saveMsg.style.opacity = "1";
    
        setTimeout(() => {
            saveMsg.style.opacity = "0";
            }, 2000);
        }}
    }

function clickToEdit() {
    newQuote.contentEditable = "true";
    newQuote.focus();
    editButton.removeAttribute('hidden');
}

function showButton() {
    editButton.removeAttribute('hidden');
}

function hideButton() {
    editButton.setAttribute('hidden', 'true');
}

newQuote.addEventListener('click', clickToEdit);
newQuote.addEventListener('mouseover', showButton);
newQuote.addEventListener('mouseleave', hideButton);
newQuote.addEventListener('keydown', handleInputKey);