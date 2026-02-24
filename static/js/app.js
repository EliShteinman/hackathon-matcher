function route() {
    Match.stopPolling();
    Admin.stopPolling();

    const hash = Utils.getHashRoute();

    if (hash.startsWith('/approve/')) {
        const uuid = hash.replace('/approve/', '');
        Match.renderApprove(uuid);
        return;
    }
    if (hash.startsWith('/reject/')) {
        const uuid = hash.replace('/reject/', '');
        Match.renderApprove(uuid);
        return;
    }

    switch (hash) {
        case '/login':
            Auth.renderLogin();
            break;
        case '/admin':
            Auth.renderAdminLogin();
            break;
        case '/admin/dashboard':
            Admin.renderDashboard();
            break;
        case '/dashboard':
            Match.renderDashboard();
            break;
        default: {
            const user = Auth.getUser();
            if (user) {
                window.location.hash = '#/dashboard';
            } else {
                window.location.hash = '#/login';
            }
        }
    }
}

window.addEventListener('hashchange', route);
window.addEventListener('DOMContentLoaded', route);

document.getElementById('btn-logout')?.addEventListener('click', () => Auth.logout());
