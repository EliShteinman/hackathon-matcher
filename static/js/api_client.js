const Api = {
    async request(method, url, body = null) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        if (response.status === 401) {
            localStorage.removeItem('user');
            localStorage.removeItem('admin');
            window.location.hash = '#/login';
            throw new Error('פג תוקף ההתחברות');
        }
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || 'שגיאה לא צפויה');
        }
        return data;
    },

    async uploadFile(url, file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || 'שגיאה בהעלאת הקובץ');
        }
        return data;
    },

    login(idNumber, email) {
        return this.request('POST', '/api/auth/login', { id_number: idNumber, email });
    },

    adminLogin(username, password) {
        return this.request('POST', '/api/auth/admin/login', { username, password });
    },

    logout() {
        return this.request('POST', '/api/auth/logout');
    },

    getMe() {
        return this.request('GET', '/api/users/me');
    },

    getAvailableUsers() {
        return this.request('GET', '/api/users/available');
    },

    createMatch(targetUserId) {
        return this.request('POST', '/api/matches', { target_user_id: targetUserId });
    },

    cancelMatch(matchId) {
        return this.request('DELETE', `/api/matches/${matchId}`);
    },

    getTokenDetails(uuid) {
        return this.request('GET', `/api/tokens/${uuid}/details`);
    },

    approveToken(uuid) {
        return this.request('POST', `/api/tokens/${uuid}/approve`);
    },

    rejectToken(uuid) {
        return this.request('POST', `/api/tokens/${uuid}/reject`);
    },

    getMetrics() {
        return this.request('GET', '/api/admin/metrics');
    },

    getAdminSettings() {
        return this.request('GET', '/api/admin/settings');
    },

    updateSettings(data) {
        return this.request('PUT', '/api/admin/settings', data);
    },

    uploadExcel(file) {
        return this.uploadFile('/api/admin/excel/upload', file);
    },

    getAdminUsers() {
        return this.request('GET', '/api/admin/users');
    },
};
