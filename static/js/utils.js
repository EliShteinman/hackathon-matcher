const Utils = {
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    },

    getStatusLabel(status) {
        const labels = {
            available: 'זמין',
            pending: 'ממתין',
            matched: 'מותאם',
        };
        return labels[status] || status;
    },

    getStatusClass(status) {
        return `status-badge status-${status}`;
    },

    setContent(html) {
        document.getElementById('app-content').innerHTML = html;
    },

    showNavbar(userName) {
        const navbar = document.getElementById('navbar');
        navbar.classList.remove('hidden');
        document.getElementById('nav-user-name').textContent = userName;
    },

    hideNavbar() {
        document.getElementById('navbar').classList.add('hidden');
    },

    getHashRoute() {
        const hash = window.location.hash.replace('#', '');
        return hash || '/';
    },
};
