/* ===== ShifaBot Report JavaScript ===== */

// The print functionality is handled by window.print() inline.
// This file provides additional report utilities.

document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard shortcut for printing (Ctrl+P already works natively)
    // No additional logic needed - browser handles it

    // Smooth scroll to sections if hash is present
    if (window.location.hash) {
        const target = document.querySelector(window.location.hash);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
});
