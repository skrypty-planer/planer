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

    <EditProfileModal
      v-model="showEditProfile"
      :user="user"
      @updated="handleProfileUpdated"
    />

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
  
  if (!user.value && route.path !== '/login' && route.path !== '/register') {
    router.push('/login')
  }
})

watch(() => route.path, () => {
  user.value = getCurrentUser()
})

const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

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