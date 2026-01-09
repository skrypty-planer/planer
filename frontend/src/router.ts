import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { getCurrentUser } from './services/auth'
import Home from './pages/Home.vue'
import Transactions from './pages/Transactions.vue'
import Analytics from './pages/Analytics.vue'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'

const routes: RouteRecordRaw[] = [
    { path: '/login', component: Login, name: 'login', meta: { requiresGuest: true } },
    { path: '/register', component: Register, name: 'register', meta: { requiresGuest: true } },
    { path: '/', component: Home, name: 'home', meta: { requiresAuth: true } },
    { path: '/transactions', component: Transactions, name: 'transactions', meta: { requiresAuth: true } },
    { path: '/analytics', component: Analytics, name: 'analytics', meta: { requiresAuth: true } },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Zabezpieczenie logowania
router.beforeEach((to, from, next) => {
    const currentUser = getCurrentUser()

    if (to.meta.requiresAuth && !currentUser) {
        next('/login')
    } else if (to.meta.requiresGuest && currentUser) {
        next('/')
    } else {
        next()
    }
})

export default router