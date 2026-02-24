let adminPollInterval = null;

const Admin = {
    async renderDashboard() {
        Utils.hideNavbar();
        if (!Auth.isAdmin()) { window.location.hash = '#/admin'; return; }

        Utils.setContent('<div class="text-center py-8"><div class="spinner"></div></div>');

        try {
            const [metrics, settings, users] = await Promise.all([
                Api.getMetrics(),
                Api.getAdminSettings(),
                Api.getAdminUsers(),
            ]);

            Utils.setContent(`
                <div class="space-y-6">
                    <div class="flex justify-between items-center">
                        <h1 class="text-2xl font-bold text-gray-800">לוח בקרה - מנהל</h1>
                        <button id="btn-admin-logout" class="text-sm text-gray-500 hover:text-gray-700">התנתק</button>
                    </div>

                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="metric-card">
                            <div class="metric-value text-green-600">${metrics.available}</div>
                            <div class="metric-label">זמינים</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value text-amber-600">${metrics.pending}</div>
                            <div class="metric-label">ממתינים</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value text-blue-600">${metrics.matched}</div>
                            <div class="metric-label">מותאמים</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value text-gray-600">${metrics.total}</div>
                            <div class="metric-label">סה"כ</div>
                        </div>
                    </div>

                    <div class="card">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">הגדרות מערכת</h3>
                        <div class="grid md:grid-cols-2 gap-4">
                            <div>
                                <label class="flex items-center gap-3 cursor-pointer">
                                    <input type="checkbox" id="global-lock" class="w-5 h-5 rounded"
                                        ${settings.is_globally_locked ? 'checked' : ''}>
                                    <span class="text-gray-700 font-medium">נעילה גלובלית</span>
                                </label>
                                <p class="text-sm text-gray-500 mt-1 mr-8">מונע כל פעולות התאמה</p>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">מועד אחרון</label>
                                <input type="datetime-local" id="deadline-input" class="input-field"
                                    value="${settings.deadline ? new Date(settings.deadline).toISOString().slice(0, 16) : ''}">
                            </div>
                        </div>
                        <button id="btn-save-settings" class="btn-primary mt-4">שמור הגדרות</button>
                    </div>

                    <div class="card">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">העלאת קובץ Excel</h3>
                        <div class="flex items-center gap-4">
                            <input type="file" id="excel-file" accept=".xlsx,.xls" class="input-field flex-1">
                            <button id="btn-upload" class="btn-primary">העלה</button>
                        </div>
                        <div id="upload-result" class="mt-2 text-sm hidden"></div>
                        ${settings.last_excel_upload_at ? `
                            <p class="text-xs text-gray-400 mt-2">
                                העלאה אחרונה: ${new Date(settings.last_excel_upload_at).toLocaleString('he-IL')}
                            </p>
                        ` : ''}
                    </div>

                    <div class="card">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">רשימת משתתפים (${users.length})</h3>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead>
                                    <tr class="border-b border-gray-200">
                                        <th class="text-right py-2 px-2">שם</th>
                                        <th class="text-right py-2 px-2">סניף</th>
                                        <th class="text-right py-2 px-2">אימייל</th>
                                        <th class="text-right py-2 px-2">סטטוס</th>
                                        <th class="text-right py-2 px-2">שותף/ה</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${users.map(u => `
                                        <tr class="border-b border-gray-100 hover:bg-gray-50">
                                            <td class="py-2 px-2">${u.full_name}</td>
                                            <td class="py-2 px-2">${u.branch}</td>
                                            <td class="py-2 px-2 text-xs">${u.email}</td>
                                            <td class="py-2 px-2">
                                                <span class="${Utils.getStatusClass(u.status)}">${Utils.getStatusLabel(u.status)}</span>
                                            </td>
                                            <td class="py-2 px-2">${u.partner_name || '-'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `);

            this.bindEvents();
        } catch (err) {
            Utils.showToast(err.message, 'error');
        }
    },

    bindEvents() {
        document.getElementById('btn-admin-logout')?.addEventListener('click', () => {
            localStorage.removeItem('admin');
            window.location.hash = '#/admin';
        });

        document.getElementById('btn-save-settings')?.addEventListener('click', async () => {
            const isLocked = document.getElementById('global-lock').checked;
            const deadlineVal = document.getElementById('deadline-input').value;
            try {
                await Api.updateSettings({
                    is_globally_locked: isLocked,
                    deadline: deadlineVal ? new Date(deadlineVal).toISOString() : null,
                });
                Utils.showToast('ההגדרות נשמרו', 'success');
            } catch (err) {
                Utils.showToast(err.message, 'error');
            }
        });

        document.getElementById('btn-upload')?.addEventListener('click', async () => {
            const fileInput = document.getElementById('excel-file');
            const resultDiv = document.getElementById('upload-result');
            if (!fileInput.files.length) {
                Utils.showToast('יש לבחור קובץ', 'error');
                return;
            }
            try {
                const data = await Api.uploadExcel(fileInput.files[0]);
                resultDiv.textContent = data.message;
                resultDiv.className = 'mt-2 text-sm text-green-600';
                resultDiv.classList.remove('hidden');
                setTimeout(() => this.renderDashboard(), 1500);
            } catch (err) {
                resultDiv.textContent = err.message;
                resultDiv.className = 'mt-2 text-sm text-red-600';
                resultDiv.classList.remove('hidden');
            }
        });

        this.startPolling();
    },

    startPolling() {
        this.stopPolling();
        adminPollInterval = setInterval(() => this.renderDashboard(), 10000);
    },

    stopPolling() {
        if (adminPollInterval) {
            clearInterval(adminPollInterval);
            adminPollInterval = null;
        }
    },
};
