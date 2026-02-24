let pollInterval = null;

const Match = {
    async renderDashboard() {
        const user = Auth.getUser();
        if (!user) { window.location.hash = '#/login'; return; }

        Utils.showNavbar(user.full_name);
        Utils.setContent('<div class="text-center py-8"><div class="spinner"></div></div>');

        try {
            const me = await Api.getMe();
            localStorage.setItem('user', JSON.stringify({
                id: me.id, full_name: me.full_name, status: me.status,
            }));

            if (me.status === 'pending') {
                this.renderPending(me);
            } else if (me.status === 'matched') {
                this.renderMatched(me);
            } else {
                await this.renderAvailable(me);
            }
        } catch (err) {
            Utils.showToast(err.message, 'error');
        }
    },

    async renderAvailable(me) {
        this.stopPolling();
        let users = [];
        try {
            users = await Api.getAvailableUsers();
        } catch (err) {
            Utils.showToast(err.message, 'error');
        }

        Utils.setContent(`
            <div class="card max-w-xl mx-auto">
                <div class="text-center mb-6">
                    <span class="${Utils.getStatusClass('available')}">${Utils.getStatusLabel('available')}</span>
                    <h2 class="text-xl font-bold text-gray-800 mt-3">שלום ${me.full_name}</h2>
                    <p class="text-gray-500 mt-1">בחר/י שותף/ה להאקתון</p>
                </div>
                ${users.length === 0 ? `
                    <p class="text-center text-gray-500 py-4">אין משתתפים זמינים כרגע</p>
                ` : `
                    <div class="space-y-4">
                        <select id="partner-select" class="input-field">
                            <option value="">-- בחר/י שותף/ה --</option>
                            ${users.map(u => `<option value="${u.id}">${u.display}</option>`).join('')}
                        </select>
                        <button id="btn-send-request" class="btn-primary w-full" disabled>שלח בקשת שותפות</button>
                    </div>
                `}
            </div>
        `);

        const select = document.getElementById('partner-select');
        const btn = document.getElementById('btn-send-request');
        if (select && btn) {
            select.addEventListener('change', () => {
                btn.disabled = !select.value;
            });
            btn.addEventListener('click', async () => {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner"></span>';
                try {
                    await Api.createMatch(parseInt(select.value));
                    Utils.showToast('הבקשה נשלחה בהצלחה!', 'success');
                    this.renderDashboard();
                } catch (err) {
                    Utils.showToast(err.message, 'error');
                    btn.disabled = false;
                    btn.textContent = 'שלח בקשת שותפות';
                }
            });
        }
    },

    renderPending(me) {
        const info = me.match_info;
        const isInitiator = info?.is_initiator;

        Utils.setContent(`
            <div class="card max-w-xl mx-auto text-center">
                <span class="${Utils.getStatusClass('pending')}">${Utils.getStatusLabel('pending')}</span>
                <h2 class="text-xl font-bold text-gray-800 mt-4">ממתין לאישור</h2>
                <div class="bg-amber-50 rounded-xl p-6 mt-4">
                    <p class="text-gray-700">
                        ${isInitiator
                            ? `שלחת בקשת שותפות ל<strong>${info.partner_name}</strong> (${info.partner_branch})`
                            : `<strong>${info.partner_name}</strong> (${info.partner_branch}) שלח/ה לך בקשת שותפות`
                        }
                    </p>
                    <p class="text-gray-500 text-sm mt-2">
                        ${isInitiator ? 'ממתין לתשובה...' : 'בדוק/י את האימייל שלך לאישור או דחייה'}
                    </p>
                </div>
                ${isInitiator && info ? `
                    <button id="btn-cancel" class="btn-danger mt-6">ביטול בקשה</button>
                ` : ''}
                <p class="text-xs text-gray-400 mt-4">העמוד מתעדכן אוטומטית</p>
            </div>
        `);

        if (isInitiator && info) {
            document.getElementById('btn-cancel')?.addEventListener('click', async () => {
                if (!confirm('האם אתה בטוח שברצונך לבטל את הבקשה?')) return;
                try {
                    await Api.cancelMatch(info.match_id);
                    Utils.showToast('הבקשה בוטלה', 'info');
                    this.renderDashboard();
                } catch (err) {
                    Utils.showToast(err.message, 'error');
                }
            });
        }

        this.startPolling();
    },

    renderMatched(me) {
        this.stopPolling();
        const info = me.match_info;

        Utils.setContent(`
            <div class="card max-w-xl mx-auto text-center">
                <span class="${Utils.getStatusClass('matched')}">${Utils.getStatusLabel('matched')}</span>
                <h2 class="text-xl font-bold text-gray-800 mt-4">יש לך שותף/ה!</h2>
                <div class="bg-blue-50 rounded-xl p-6 mt-4 text-right">
                    <h3 class="font-semibold text-gray-800 mb-3">פרטי השותף/ה:</h3>
                    <p class="text-gray-700"><strong>שם:</strong> ${info.partner_name}</p>
                    <p class="text-gray-700"><strong>סניף:</strong> ${info.partner_branch}</p>
                    ${info.partner_email ? `<p class="text-gray-700"><strong>אימייל:</strong> ${info.partner_email}</p>` : ''}
                    ${info.partner_class_name ? `<p class="text-gray-700"><strong>כיתה:</strong> ${info.partner_class_name}</p>` : ''}
                </div>
                ${info.is_initiator ? `
                    <button id="btn-cancel-matched" class="btn-danger mt-6">ביטול שותפות</button>
                ` : ''}
            </div>
        `);

        if (info.is_initiator) {
            document.getElementById('btn-cancel-matched')?.addEventListener('click', async () => {
                if (!confirm('האם אתה בטוח שברצונך לבטל את השותפות?')) return;
                try {
                    await Api.cancelMatch(info.match_id);
                    Utils.showToast('השותפות בוטלה', 'info');
                    this.renderDashboard();
                } catch (err) {
                    Utils.showToast(err.message, 'error');
                }
            });
        }
    },

    async renderApprove(tokenUuid) {
        Utils.hideNavbar();
        Utils.setContent('<div class="text-center py-8"><div class="spinner"></div></div>');

        try {
            const details = await Api.getTokenDetails(tokenUuid);

            if (details.is_used || details.is_expired) {
                Utils.setContent(`
                    <div class="card max-w-xl mx-auto text-center">
                        <h2 class="text-xl font-bold text-gray-800 mb-4">
                            ${details.is_expired ? 'פג תוקף הקישור' : 'הקישור כבר נוצל'}
                        </h2>
                        <p class="text-gray-500">לא ניתן לבצע פעולה זו.</p>
                    </div>
                `);
                return;
            }

            Utils.setContent(`
                <div class="card max-w-xl mx-auto text-center">
                    <h2 class="text-xl font-bold text-gray-800 mb-2">בקשת שותפות</h2>
                    <p class="text-gray-600 mb-6">
                        <strong>${details.initiator_name}</strong> מסניף <strong>${details.initiator_branch}</strong>
                        רוצה להיות השותף/ה שלך בהאקתון
                    </p>
                    <div class="flex gap-4 justify-center">
                        <button id="btn-approve" class="btn-success text-lg px-8">אישור</button>
                        <button id="btn-reject" class="btn-danger text-lg px-8">דחייה</button>
                    </div>
                    <div id="approve-result" class="mt-4 hidden"></div>
                </div>
            `);

            document.getElementById('btn-approve').addEventListener('click', async () => {
                try {
                    const result = await Api.approveToken(tokenUuid);
                    document.getElementById('approve-result').innerHTML = `
                        <div class="bg-green-50 text-green-800 p-4 rounded-lg">${result.message}</div>
                    `;
                    document.getElementById('approve-result').classList.remove('hidden');
                    document.getElementById('btn-approve').remove();
                    document.getElementById('btn-reject').remove();
                } catch (err) {
                    Utils.showToast(err.message, 'error');
                }
            });

            document.getElementById('btn-reject').addEventListener('click', async () => {
                if (!confirm('האם אתה בטוח שברצונך לדחות את הבקשה?')) return;
                try {
                    const result = await Api.rejectToken(tokenUuid);
                    document.getElementById('approve-result').innerHTML = `
                        <div class="bg-red-50 text-red-800 p-4 rounded-lg">${result.message}</div>
                    `;
                    document.getElementById('approve-result').classList.remove('hidden');
                    document.getElementById('btn-approve').remove();
                    document.getElementById('btn-reject').remove();
                } catch (err) {
                    Utils.showToast(err.message, 'error');
                }
            });
        } catch (err) {
            Utils.setContent(`
                <div class="card max-w-xl mx-auto text-center">
                    <h2 class="text-xl font-bold text-red-600 mb-4">שגיאה</h2>
                    <p class="text-gray-500">${err.message}</p>
                </div>
            `);
        }
    },

    startPolling() {
        this.stopPolling();
        pollInterval = setInterval(() => this.renderDashboard(), 5000);
    },

    stopPolling() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    },
};
