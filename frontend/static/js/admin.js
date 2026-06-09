/**
 * ShifaBot - Admin Panel JavaScript
 * Shared utilities for all admin pages.
 */

/* ===== Sidebar Toggle (mobile) ===== */
function toggleSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
}

/* ===== HTML Escape ===== */
function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ===== Date Formatters ===== */
function formatDate(isoString) {
    if (!isoString) return '--';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDateFull(isoString) {
    if (!isoString) return '--';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

/* ===== Toast Override for Admin (handles string category) ===== */
function showToast(message, category) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMessage');
    if (!toast || !toastMsg) return;

    const isError = (category === 'danger' || category === 'error' || category === true);
    const icon = isError ? 'bi-exclamation-circle' : 'bi-check-circle';
    toastMsg.innerHTML = `<strong><i class="bi ${icon} me-1"></i></strong> ${message}`;
    toast.className = isError ? 'toast-shifabot error' : 'toast-shifabot';
    toast.style.display = 'block';

    setTimeout(() => { toast.style.display = 'none'; }, 4000);
}
