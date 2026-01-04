// Authentication service using localStorage

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
    password: string  // Added for profile editing
}

const USERS_KEY = 'budget_planner_users'
const SESSION_KEY = 'budget_planner_session'
const GUEST_USER_ID = 'guest-user'

// Generate a simple SVG avatar with initials
function generateAvatar(username: string): string {
    const colors = [
        '#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5',
        '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
        '#8BC34A', '#CDDC39', '#FFC107', '#FF9800', '#FF5722'
    ];
    // Simple hash for color consistency
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    const color = colors[Math.abs(hash) % colors.length];
    const initial = username.charAt(0).toUpperCase();

    const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <rect width="100" height="100" fill="${color}" />
        <text x="50" y="50" dy=".35em" font-size="50" font-family="Arial, sans-serif" font-weight="bold" text-anchor="middle" fill="white">${initial}</text>
    </svg>`;

    return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

// Initialize with guest user
function initializeUsers() {
    const users = getUsers()
    if (!users[GUEST_USER_ID]) {
        users[GUEST_USER_ID] = {
            id: GUEST_USER_ID,
            username: 'Gość',
            password: '',
            avatarUrl: generateAvatar('Gość')
        }
        saveUsers(users)
    }
}

function getUsers(): Record<string, User> {
    const data = localStorage.getItem(USERS_KEY)
    return data ? JSON.parse(data) : {}
}

function saveUsers(users: Record<string, User>) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users))
}

// Password validation
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

// Register new user
export async function register(
    username: string,
    password: string,
    avatarUrl?: string
): Promise<{ success: boolean; error?: string; user?: UserSession }> {
    initializeUsers()
    const users = getUsers()

    // Check if username already exists
    const existingUser = Object.values(users).find(
        u => u.username.toLowerCase() === username.toLowerCase()
    )
    if (existingUser) {
        return { success: false, error: 'Użytkownik o tej nazwie już istnieje' }
    }

    // Validate password
    const passwordCheck = validatePassword(password)
    if (!passwordCheck.valid) {
        return { success: false, error: passwordCheck.error }
    }

    // Create new user
    const userId = `user-${Date.now()}`
    const newUser: User = {
        id: userId,
        username,
        password, // In production, this should be hashed!
        avatarUrl: avatarUrl || generateAvatar(username)
    }

    users[userId] = newUser
    saveUsers(users)

    // Auto-login
    const session: UserSession = {
        id: newUser.id,
        username: newUser.username,
        avatarUrl: newUser.avatarUrl,
        password: newUser.password
    }
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))

    return { success: true, user: session }
}

// Login
export async function login(
    username: string,
    password: string
): Promise<{ success: boolean; error?: string; user?: UserSession }> {
    initializeUsers()
    const users = getUsers()

    const user = Object.values(users).find(
        u => u.username.toLowerCase() === username.toLowerCase()
    )

    if (!user) {
        return { success: false, error: 'Nieprawidłowa nazwa użytkownika lub hasło' }
    }

    if (user.password !== password) {
        return { success: false, error: 'Nieprawidłowa nazwa użytkownika lub hasło' }
    }

    const session: UserSession = {
        id: user.id,
        username: user.username,
        avatarUrl: user.avatarUrl,
        password: user.password
    }
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))

    return { success: true, user: session }
}

// Login as guest
export async function loginAsGuest(): Promise<{ success: boolean; user?: UserSession }> {
    initializeUsers()
    const users = getUsers()
    const guestUser = users[GUEST_USER_ID]

    // Ensure guest has an avatar if it was missing (legacy fix)
    if (!guestUser.avatarUrl) {
        guestUser.avatarUrl = generateAvatar('Gość')
        users[GUEST_USER_ID] = guestUser
        saveUsers(users)
    }

    const session: UserSession = {
        id: guestUser.id,
        username: guestUser.username,
        avatarUrl: guestUser.avatarUrl,
        password: guestUser.password
    }
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))

    return { success: true, user: session }
}

// Logout
export async function logout(): Promise<void> {
    localStorage.removeItem(SESSION_KEY)
}

// Get current user session
export function getCurrentUser(): UserSession | null {
    const data = localStorage.getItem(SESSION_KEY)
    return data ? JSON.parse(data) : null
}

// Update user profile
export async function updateProfile(
    userId: string,
    updates: { username?: string; password?: string; avatarUrl?: string }
): Promise<{ success: boolean; error?: string; user?: UserSession }> {
    const users = getUsers()
    const user = users[userId]

    if (!user) {
        return { success: false, error: 'Użytkownik nie znaleziony' }
    }

    // Check if new username is taken
    if (updates.username && updates.username !== user.username) {
        const existingUser = Object.values(users).find(
            u => u.id !== userId && u.username.toLowerCase() === updates.username!.toLowerCase()
        )
        if (existingUser) {
            return { success: false, error: 'Nazwa użytkownika jest już zajęta' }
        }
        user.username = updates.username

        // Regenerate avatar if username changed and no custom avatar provided
        if (!updates.avatarUrl && !user.avatarUrl.startsWith('data:')) {
            user.avatarUrl = generateAvatar(user.username)
        }
    }

    // Validate new password if provided
    if (updates.password) {
        const passwordCheck = validatePassword(updates.password)
        if (!passwordCheck.valid) {
            return { success: false, error: passwordCheck.error }
        }
        user.password = updates.password
    }

    if (updates.avatarUrl) {
        user.avatarUrl = updates.avatarUrl
    } else if (updates.username && !updates.avatarUrl) {
        // If username changed but no new avatar, and old one was generated, regenerate
        // Simple check: if it's an SVG data URI, we assume it's generated. 
        // If user uploaded a photo, it would be a base64 image (also data URI), but we can't easily distinguish.
        // For now, let's just respect the passed avatarUrl. If it's null, we keep the old one unless we want to force regenerate.
        // The logic above (lines 202-204) handles regeneration if needed.
    }

    users[userId] = user
    saveUsers(users)

    // Update session
    const session: UserSession = {
        id: user.id,
        username: user.username,
        avatarUrl: user.avatarUrl,
        password: user.password
    }
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))

    return { success: true, user: session }
}
