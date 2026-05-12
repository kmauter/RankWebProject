/**
 * Wrapper around fetch that handles 401 responses globally.
 * If any API call returns 401, clears the auth token and redirects to login.
 *
 * Can be used as a drop-in replacement for fetch, or installed globally
 * by calling installGlobal401Handler() once at app startup.
 */
export async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('authToken');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        localStorage.removeItem('authToken');
        window.location.href = '/';
        return response;
    }

    return response;
}

/**
 * Installs a global interceptor on window.fetch that redirects to login
 * on any 401 response from /api/* endpoints.
 * Call this once at app startup (e.g., in index.js).
 */
export function installGlobal401Handler() {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        const response = await originalFetch(...args);
        const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
        if (response.status === 401 && url.includes('/api/')) {
            localStorage.removeItem('authToken');
            window.location.href = '/';
        }
        return response;
    };
}
