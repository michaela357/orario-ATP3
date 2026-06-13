document.querySelector('#flashcard-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formElement = e.target;
    const targetUrl = formElement.getAttribute('action') || '/generate-flashcards';

    // Call your postForm helper using the exact string URL path
    const result = await postForm(targetUrl, formElement);

    if (!result) return;

    if (!result.success) {
        showError(result.error);
    } else if (result.success && result.redirect) {
        window.location.href = result.redirect;
    }
});