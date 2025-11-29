import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Home from './pages/Home.vue'
import Transactions from './pages/Transactions.vue'
import Analytics from './pages/Analytics.vue'

const routes: RouteRecordRaw[] = [
    { path: '/', component: Home, name: 'home' },
    { path: '/transactions', component: Transactions, name: 'transactions' },
    { path: '/analytics', component: Analytics, name: 'analytics' },
]

export default createRouter({
    history: createWebHistory(),
    routes,
})