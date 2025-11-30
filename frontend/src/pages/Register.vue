<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Budżet Planner</h1>
        <p class="auth-subtitle">Utwórz nowe konto</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
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
          <p class="form-hint">
            Hasło musi zawierać: min. 8 znaków, dużą literę, cyfrę i znak specjalny
          </p>
        </div>

        <div class="form-group">
          <label class="form-label">Zdjęcie profilowe (opcjonalne)</label>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="form-file-input"
            @change="handleFileChange"
          />
          <div v-if="avatarPreview" class="avatar-preview">
            <img :src="avatarPreview" alt="Preview" />
          </div>
        </div>

        <span v-if="errors.general" class="form-error" style="display: block; margin-bottom: 1rem;">
          {{ errors.general }}
        </span>

        <button type="submit" class="btn btn-success btn-full">
          Zarejestruj się
        </button>
      </form>

      <p class="auth-footer">
        Masz już konto? 
        <router-link to="/login" class="auth-link">Zaloguj się</router-link>
      </p>
    </div>

    <Modal
      v-model="showSuccessModal"
      title="Konto utworzone!"
      message="Twoje konto zostało pomyślnie utworzone. Zalogowaliśmy Cię automatycznie."
      :show-cancel="false"
      :show-confirm="true"
      confirm-text="Przejdź do aplikacji"
      confirm-class="btn-success"
      @confirm="closeSuccessModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../services/auth'
import Modal from '../components/Modal.vue'

const router = useRouter()

const username = ref('')
const password = ref('')
const avatarPreview = ref('')
const avatarDataUrl = ref('')
const errors = ref<{ username?: string; password?: string; general?: string }>({})
const showSuccessModal = ref(false)
const fileInput = ref<HTMLInputElement>()

// Redirect when modal closes (either by OK button or backdrop click)
import { watch } from 'vue'
watch(showSuccessModal, (isOpen) => {
  if (!isOpen) {
    router.push('/')
  }
})

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string
      avatarDataUrl.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

async function handleRegister() {
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

  const result = await register(username.value, password.value, avatarDataUrl.value)
  
  if (result.success) {
    showSuccessModal.value = true
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } else {
    errors.value.general = result.error
  }
}

function closeSuccessModal() {
  showSuccessModal.value = false
  router.push('/')
}

</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); /* Green gradient */
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

.form-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
  margin-bottom: 0;
}

.avatar-preview {
  margin-top: 0.5rem;
  text-align: center;
}

.avatar-preview img {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 2px solid var(--primary);
  object-fit: cover;
}

.btn-full {
  width: 100%;
  padding: 0.65rem;
  font-size: 0.95rem;
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

