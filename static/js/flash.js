const flashContainer = document.getElementById('flash-messages');
const inputs = document.querySelectorAll('input[name="email"], input[name="password"]');

inputs.forEach(input => {
    input.addEventListener('input', () => {
        if (flashContainer) {
            flashContainer.style.display = 'none';
        }
    });
});