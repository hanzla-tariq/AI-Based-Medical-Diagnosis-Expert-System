/* ===== ShifaBot Main JavaScript ===== */

// Show/hide loading spinner
function showSpinner(message) {
    const overlay = document.getElementById('spinnerOverlay');
    if (overlay) {
        if (message) {
            overlay.querySelector('p').textContent = message;
        }
        overlay.classList.add('active');
    }
}

function hideSpinner() {
    const overlay = document.getElementById('spinnerOverlay');
    if (overlay) overlay.classList.remove('active');
}

// Toast notification
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMessage');
    if (!toast || !toastMsg) return;

    toastMsg.innerHTML = `<strong>${isError ? '<i class="bi bi-exclamation-circle me-1"></i>' : '<i class="bi bi-check-circle me-1"></i>'}</strong> ${message}`;
    toast.className = isError ? 'toast-shifabot error' : 'toast-shifabot';
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 4000);
}

// API helper
async function apiCall(url, method = 'POST', data = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (data) options.body = JSON.stringify(data);

    const response = await fetch(url, options);
    const result = await response.json();
    return { status: response.status, data: result };
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

// Auto-dismiss alerts
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
