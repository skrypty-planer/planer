<template>
  <Modal
    v-model="isOpen"
    title="Edytuj profil"
    :show-cancel="false"
    :show-confirm="false"
  >
    <form @submit.prevent="handleSave" class="profile-form">
      <div class="form-group">
        <label class="form-label">Nazwa użytkownika</label>
        <input
          v-model="formData.username"
          type="text"
          class="form-input"
          :class="{ error: errors.username }"
          placeholder="Wprowadź nazwę użytkownika"
        />
        <span v-if="errors.username" class="form-error">{{ errors.username }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">Hasło</label>
        <div class="password-input-wrapper">
          <input
            v-model="formData.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-input"
            :class="{ error: errors.password }"
            placeholder="Wprowadź hasło"
          />
          <button 
            type="button" 
            class="password-toggle-btn" 
            @click="showPassword = !showPassword"
            :title="showPassword ? 'Ukryj hasło' : 'Pokaż hasło'"
          >
            <span v-if="showPassword">👁️</span>
            <span v-else>🙈</span>
          </button>
        </div>
        <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">Zdjęcie profilowe</label>
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

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="handleCancel">
          Anuluj
        </button>
        <button type="submit" class="btn btn-success">
          Zapisz zmiany
        </button>
      </div>
    </form>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { updateProfile } from '../services/auth'
import type { UserSession } from '../services/auth'
import Modal from './Modal.vue'

const props = defineProps<{
  modelValue: boolean
  user: UserSession | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'updated': [user: UserSession]
}>()

const isOpen = ref(props.modelValue)
const formData = ref({
  username: '',
  password: '',
})
const avatarPreview = ref('')
const avatarDataUrl = ref('')
const errors = ref<{ username?: string; password?: string; general?: string }>({})
const fileInput = ref<HTMLInputElement>()
const showPassword = ref(false)

watch(() => props.modelValue, (value) => {
  isOpen.value = value
  if (value && props.user) {
    formData.value.username = props.user.username
    // Populate password field with current password
    formData.value.password = props.user.password || ''
    avatarPreview.value = props.user.avatarUrl
    avatarDataUrl.value = ''
    errors.value = {}
  }
})

watch(isOpen, (value) => {
  emit('update:modelValue', value)
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

async function handleSave() {
  if (!props.user) return

  // Reset errors
  errors.value = {}

  // Validate
  if (!formData.value.username.trim()) {
    errors.value.username = 'Pole obligatoryjne'
    return
  }

  const updates: { username?: string; password?: string; avatarUrl?: string } = {}

  if (formData.value.username !== props.user.username) {
    updates.username = formData.value.username
  }

  if (formData.value.password.trim()) {
    // Check if password is the same as current
    if (formData.value.password === props.user.password) {
      errors.value.password = 'Nowe hasło jest takie samo jak obecne'
      return
    }
    updates.password = formData.value.password
  }

  if (avatarDataUrl.value) {
    updates.avatarUrl = avatarDataUrl.value
  }

  const result = await updateProfile(props.user.id, updates)
  
  if (result.success && result.user) {
    emit('updated', result.user)
    isOpen.value = false
  } else {
    errors.value.general = result.error
  }
}

function handleCancel() {
  isOpen.value = false
}
</script>

<style scoped>
.profile-form {
  margin: 0;
}

.avatar-preview {
  margin-top: 1rem;
  text-align: center;
}

.avatar-preview img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid var(--primary);
  object-fit: cover;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper .form-input {
  padding-right: 3rem;
}

.password-toggle-btn {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.password-toggle-btn:hover {
  opacity: 0.7;
}
</style>
