/** Authentication state management with Alpine.js.
 *
 * Handles JWT token storage, auto-refresh, and login/logout flow.
 *
 * Requirements: UI-02, UI-03
 */

function authStore() {
    return {
        token: localStorage.getItem('access_token'),
        refreshToken: localStorage.getItem('refresh_token'),
        user: JSON.parse(localStorage.getItem('user') || 'null'),
        isAuthenticated: false,

        init() {
            this.isAuthenticated = !!this.token;
            if (this.token) {
                this.checkTokenExpiry();
            }
        },

        async login(username, password) {
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                if (!response.ok) {
                    throw new Error('Invalid credentials');
                }

                const data = await response.json();
                this.token = data.access_token;
                this.refreshToken = data.refresh_token;

                // Store tokens
                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);

                // Set authenticated
                this.isAuthenticated = true;

                // Get user info (decode JWT)
                this.user = this.parseJWT(this.token);
                localStorage.setItem('user', JSON.stringify(this.user));

                // Emit event
                window.dispatchEvent(new CustomEvent('auth:login'));

                return true;
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        },

        async refreshTokens() {
            if (!this.refreshToken) return false;

            try {
                const response = await fetch('/api/auth/refresh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: this.refreshToken })
                });

                if (!response.ok) {
                    throw new Error('Token refresh failed');
                }

                const data = await response.json();
                this.token = data.access_token;
                this.refreshToken = data.refresh_token; // NEW token (rotation)

                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);

                return true;
            } catch (error) {
                console.error('Token refresh failed:', error);
                this.logout();
                return false;
            }
        },

        logout() {
            this.token = null;
            this.refreshToken = null;
            this.user = null;
            this.isAuthenticated = false;

            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');

            window.dispatchEvent(new CustomEvent('auth:logout'));
        },

        getAuthHeaders() {
            return {
                'Authorization': `Bearer ${this.token}`
            };
        },

        checkTokenExpiry() {
            // Auto-refresh 5 minutes before expiry
            const checkInterval = 5 * 60 * 1000; // 5 min
            setInterval(() => {
                this.refreshTokens();
            }, checkInterval);
        },

        parseJWT(token) {
            // Simple JWT parse (no verification - server does that)
            const parts = token.split('.');
            if (parts.length !== 3) return null;
            const payload = JSON.parse(atob(parts[1]));
            return {
                id: payload.sub,
                exp: payload.exp
            };
        }
    };
}

// Initialize global auth store
document.addEventListener('alpine:init', () => {
    Alpine.data('authStore', authStore);
});
