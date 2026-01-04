<template>
  <div class="app">
    <AppHeader 
      v-if="user" 
      :user="user" 
      @edit-profile="showEditProfile = true"
      @logout="showLogoutConfirm = true"
    />

    <main :class="isAuthPage ? 'container1' : 'container'">
      <MenuNav v-if="user" />
      <router-view :user="user" :key="user?.id" />
    </main>

    <AppFooter v-if="user" />

    <!-- Edit Profile Modal -->
    <EditProfileModal
      v-model="showEditProfile"
      :user="user"
      @updated="handleProfileUpdated"
    />

    <!-- Logout Confirmation Modal -->
    <Modal
      v-model="showLogoutConfirm"
      title="Wylogowanie"
      message="Czy na pewno chcesz się wylogować?"
      :show-cancel="true"
      :show-confirm="true"
      cancel-text="Anuluj"
      confirm-text="Wyloguj"
      confirm-class="btn-danger"
      @confirm="handleLogout"
    />

    <!-- Logout Success Modal -->
    <Modal
      v-model="showLogoutSuccess"
      title="Wylogowano"
      message="Zostałeś pomyślnie wylogowany. Do zobaczenia!"
      :show-cancel="false"
      :show-confirm="true"
      confirm-text="OK"
      confirm-class="btn-primary"
      @confirm="closeLogoutSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import MenuNav from './components/MenuNav.vue'
import Modal from './components/Modal.vue'
import EditProfileModal from './components/EditProfileModal.vue'
import { getCurrentUser, logout } from './services/auth'
import type { UserSession } from './services/auth'

const router = useRouter()
const route = useRoute()

const user = ref<UserSession | null>(null)
const showEditProfile = ref(false)
const showLogoutConfirm = ref(false)
const showLogoutSuccess = ref(false)

onMounted(() => {
  user.value = getCurrentUser()
  
  // If no user and not on auth pages, redirect to login
  if (!user.value && route.path !== '/login' && route.path !== '/register') {
    router.push('/login')
  }
})

// Watch for route changes to update user state (e.g. after login/logout)
watch(() => route.path, () => {
  user.value = getCurrentUser()
})

// Check if current route is auth page
const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

// Watch for success modal closing (e.g. via backdrop) to ensure redirect
watch(showLogoutSuccess, (isOpen) => {
  if (!isOpen && !user.value) {
    router.push('/login')
  }
})

function handleProfileUpdated(updatedUser: UserSession) {
  user.value = updatedUser
}

function handleLogout() {
  logout()
  user.value = null
  showLogoutConfirm.value = false
  // Redirect immediately to login to avoid "empty data" flash
  router.push('/login')
  showLogoutSuccess.value = true
}

function closeLogoutSuccess() {
  showLogoutSuccess.value = false
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  flex: 1;
}

.container1 {
  /* width: 100%;
  max-width: 1200px; */
  min-width: 100vw;
  /* margin: 0 auto; */
  /* padding: 1.5rem; */
  flex: 1;
}
</style>