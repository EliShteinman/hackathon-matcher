const Auth = {
    renderLogin() {
        Utils.hideNavbar();
        Utils.setContent(`
            <div class="flex items-center justify-center min-h-[70vh]">
                <div class="card w-full max-w-md">
                    <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">כניסה למערכת</h2>
                    <form id="login-form" class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">תעודת זהות</label>
                            <input type="text" id="login-id" class="input-field" placeholder="הזן מספר תעודת זהות" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">אימייל</label>
                            <input type="email" id="login-email" class="input-field" placeholder="הזן כתובת אימייל" required>
                        </div>
                        <button type="submit" class="btn-primary w-full">התחבר</button>
                        <div id="login-error" class="text-red-600 text-sm text-center hidden"></div>
                    </form>
                    <div class="mt-4 pt-4 border-t border-gray-200 text-center">
                        <a href="#/admin" class="text-sm text-indigo-600 hover:text-indigo-500">כניסת מנהל</a>
                    </div>
                </div>
            </div>
        `);

        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const idNumber = document.getElementById('login-id').value.trim();
            const email = document.getElementById('login-email').value.trim();
            const errorEl = document.getElementById('login-error');
            errorEl.classList.add('hidden');

            try {
                const data = await Api.login(idNumber, email);
                localStorage.setItem('user', JSON.stringify({
                    id: data.user_id,
                    full_name: data.full_name,
                    status: data.status,
                }));
                window.location.hash = '#/dashboard';
            } catch (err) {
                errorEl.textContent = err.message;
                errorEl.classList.remove('hidden');
            }
        });
    },

    renderAdminLogin() {
        Utils.hideNavbar();
        Utils.setContent(`
            <div class="flex items-center justify-center min-h-[70vh]">
                <div class="card w-full max-w-md">
                    <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">כניסת מנהל</h2>
                    <form id="admin-login-form" class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">שם משתמש</label>
                            <input type="text" id="admin-username" class="input-field" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">סיסמה</label>
                            <input type="password" id="admin-password" class="input-field" required>
                        </div>
                        <button type="submit" class="btn-primary w-full">התחבר כמנהל</button>
                        <div id="admin-login-error" class="text-red-600 text-sm text-center hidden"></div>
                    </form>
                    <div class="mt-4 pt-4 border-t border-gray-200 text-center">
                        <a href="#/login" class="text-sm text-indigo-600 hover:text-indigo-500">חזרה לכניסה רגילה</a>
                    </div>
                </div>
            </div>
        `);

        document.getElementById('admin-login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('admin-username').value.trim();
            const password = document.getElementById('admin-password').value;
            const errorEl = document.getElementById('admin-login-error');
            errorEl.classList.add('hidden');

            try {
                await Api.adminLogin(username, password);
                localStorage.setItem('admin', 'true');
                window.location.hash = '#/admin/dashboard';
            } catch (err) {
                errorEl.textContent = err.message;
                errorEl.classList.remove('hidden');
            }
        });
    },

    async logout() {
        try { await Api.logout(); } catch { /* ignore */ }
        localStorage.removeItem('user');
        localStorage.removeItem('admin');
        window.location.hash = '#/login';
    },

    getUser() {
        const raw = localStorage.getItem('user');
        return raw ? JSON.parse(raw) : null;
    },

    isAdmin() {
        return localStorage.getItem('admin') === 'true';
    },
};
