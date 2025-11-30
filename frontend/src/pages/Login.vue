<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Budżet Planner</h1>
        <p class="auth-subtitle">Zaloguj się do swojego konta</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label class="form-label">Nazwa użytkownika *</label>
          <input
            v-model="username"
            type="text"
            class="form-input"
            :class="{ error: errors.username }"
            placeholder="Wprowadź nazwę użytkownika"
          />
          <span v-if="errors.username" class="form-error">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Hasło *</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            :class="{ error: errors.password }"
            placeholder="Wprowadź hasło"
          />
          <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
        </div>

        <span v-if="errors.general" class="form-error" style="display: block; margin-bottom: 1rem;">
          {{ errors.general }}
        </span>

        <button type="submit" class="btn btn-primary btn-full">
          Zaloguj się
        </button>
      </form>

      <div class="auth-divider">lub</div>

      <button @click="handleGuestLogin" class="btn btn-secondary btn-full">
        Zaloguj jako Gość
      </button>

      <p class="auth-footer">
        Nie masz konta? 
        <router-link to="/register" class="auth-link">Zarejestruj się</router-link>
      </p>
    </div>

    <Modal
      v-model="showSuccessModal"
      title="Pomyślnie zalogowano!"
      message="Witamy w Budżet Planner"
      :show-cancel="false"
      :show-confirm="true"
      confirm-text="OK"
      confirm-class="btn-success"
      @confirm="closeSuccessModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { login, loginAsGuest } from '../services/auth'
import Modal from '../components/Modal.vue'

const router = useRouter()

const username = ref('')
const password = ref('')
const errors = ref<{ username?: string; password?: string; general?: string }>({})
const showSuccessModal = ref(false)

// Auto-redirect after delay or when modal closes
watch(showSuccessModal, (isOpen) => {
  if (isOpen) {
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } else if (!isOpen) {
    router.push('/')
  }
})

async function handleLogin() {
  // Reset errors
  errors.value = {}

  // Validate
  let isValid = true
  if (!username.value.trim()) {
    errors.value.username = 'Pole obligatoryjne'
    isValid = false
  }
  if (!password.value.trim()) {
    errors.value.password = 'Pole obligatoryjne'
    isValid = false
  }

  if (!isValid) return

  const result = await login(username.value, password.value)
  
  if (result.success) {
    showSuccessModal.value = true
  } else {
    errors.value.general = result.error
    errors.value.password = ' '
  }
}

async function handleGuestLogin() {
  const result = await loginAsGuest()
  if (result.success) {
    showSuccessModal.value = true
  }
}

function closeSuccessModal() {
  showSuccessModal.value = false
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #56ccf2 0%, #2f80ed 100%); /* Lighter blue gradient */
  padding: 0.5rem;
  overflow: hidden;
}

.auth-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 600px;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.auth-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  color: var(--primary);
  margin: 0 0 0.4rem;
  font-weight: 700;
}

.auth-subtitle {
  color: var(--text-muted);
  margin: 0 0 1.2rem;
  font-size: 0.9rem;
}

.auth-form {
  margin-bottom: 0.8rem;
}

.btn-full {
  width: 100%;
  padding: 0.65rem;
  font-size: 0.95rem;
}

.auth-divider {
  text-align: center;
  margin: 0.8rem 0;
  color: var(--text-muted);
  position: relative;
  font-size: 0.85rem;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: var(--border);
}

.auth-divider::before {
  left: 0;
}

.auth-divider::after {
  right: 0;
}

.auth-footer {
  text-align: center;
  margin-top: 0.8rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.auth-link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>
