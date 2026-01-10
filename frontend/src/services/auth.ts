// API
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface User {
    id: string
    username: string
    password: string
    avatarUrl: string
}

export interface UserSession {
    id: string
    username: string
    avatarUrl: string
    password: string
}

const SESSION_KEY = 'budget_planner_session';

async function request(endpoint: string, options: RequestInit = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        credentials: 'include'
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        throw new Error(data.message || 'Request failed');
    }

    return data;
}

export function validatePassword(password: string): { valid: boolean; error?: string } {
    if (password.length < 8) {
        return { valid: false, error: 'Hasło musi mieć co najmniej 8 znaków' }
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, error: 'Hasło musi zawierać co najmniej jedną dużą literę' }
    }
    if (!/[0-9]/.test(password)) {
        return { valid: false, error: 'Hasło musi zawierać co najmniej jedną cyfrę' }
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        return { valid: false, error: 'Hasło musi zawierać co najmniej jeden znak specjalny' }
    }
    return { valid: true }
}

export async function register(
    username: string,
    password: string,
    avatarUrl?: string
): Promise<{ success: boolean; error?: string; user?: UserSession }> {
    try {
        const res = await request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password, avatarUrl })
        });

        const user: UserSession = {
            id: res.user.id,
            username: res.user.username,
            avatarUrl: res.user.avatarUrl,
            password
        };

        localStorage.setItem(SESSION_KEY, JSON.stringify(user));
        return { success: true, user };
    } catch (err: any) {
        return { success: false, error: err.message };
    }
}

export async function login(
    username: string,
    password: string
): Promise<{ success: boolean; error?: string; user?: UserSession }> {
    try {
        await request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        const meRes = await request('/auth/me', { method: 'GET' });
        const user: UserSession = {
            id: meRes.user.id,
            username: meRes.user.username,
            avatarUrl: meRes.user.avatarUrl,
            password: meRes.user.password
        };

        localStorage.setItem(SESSION_KEY, JSON.stringify(user));
        return { success: true, user };
    } catch (err: any) {
        return { success: false, error: err.message };
    }
}

export async function loginAsGuest(): Promise<{ success: boolean; user?: UserSession }> {
    try {
        await request('/auth/guest-login', { method: 'POST' });
        const meRes = await request('/auth/me', { method: 'GET' });
        const user: UserSession = {
            id: meRes.user.id,
            username: meRes.user.username,
            avatarUrl: meRes.user.avatarUrl,
            password: meRes.user.password
        };

        localStorage.setItem(SESSION_KEY, JSON.stringify(user));
        return { success: true, user };
    } catch (err) {
        return { success: false };
    }
}

export async function logout(): Promise<void> {
    try {
        await request('/auth/logout', { method: 'POST' });
    } catch (e) {
        console.error('Logout failed', e);
    } finally {
        localStorage.removeItem(SESSION_KEY);
        window.location.reload();
    }
}

export function getCurrentUser(): UserSession | null {
    const data = localStorage.getItem(SESSION_KEY);
    return data ? JSON.parse(data) : null;
}

export async function updateProfile(
    userId: string,
    updates: { username?: string; password?: string; avatarUrl?: string }
): Promise<{ success: boolean; error?: string; user?: UserSession }> {
    try {
        const res = await request('/auth/update-profile', {
            method: 'PUT',
            body: JSON.stringify(updates)
        });

        const user: UserSession = {
            id: res.user.id,
            username: res.user.username,
            avatarUrl: res.user.avatarUrl,
            password: res.user.password
        };

        localStorage.setItem(SESSION_KEY, JSON.stringify(user));
        return { success: true, user };
    } catch (err: any) {
        return { success: false, error: err.message };
    }
}
