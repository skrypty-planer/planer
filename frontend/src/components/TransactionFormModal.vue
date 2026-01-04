<template>
  <Modal
    v-model="isOpen"
    :title="mode === 'add' ? 'Dodaj transakcję' : 'Edytuj transakcję'"
    :show-cancel="false"
    :show-confirm="false"
  >
    <form @submit.prevent="handleSubmit" class="transaction-form">
      <div class="form-group">
        <label class="form-label">Nazwa *</label>
        <input
          v-model="formData.name"
          type="text"
          class="form-input"
          :class="{ error: errors.name }"
          placeholder="Nazwa transakcji"
        />
        <span v-if="errors.name" class="form-error">{{ errors.name }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">Typ *</label>
        <select
          v-model="formData.type"
          class="form-select"
          :class="{ error: errors.type }"
        >
          <option value="">Wybierz typ</option>
          <option value="income">Przychód</option>
          <option value="expense">Wydatek</option>
        </select>
        <span v-if="errors.type" class="form-error">{{ errors.type }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">Kwota *</label>
        <input
          v-model.number="formData.amount"
          type="number"
          step="0.01"
          class="form-input"
          :class="{ error: errors.amount }"
          placeholder="0.00"
        />
        <span v-if="errors.amount" class="form-error">{{ errors.amount }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">Kategoria *</label>
        <select
          v-model="formData.category"
          class="form-select"
          :class="{ error: errors.category }"
        >
          <option value="">Wybierz kategorię</option>
          <option v-for="cat in availableCategories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
        <span v-if="errors.category" class="form-error">{{ errors.category }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">Data *</label>
        <input
          v-model="formData.date"
          type="date"
          class="form-input"
          :class="{ error: errors.date }"
        />
        <span v-if="errors.date" class="form-error">{{ errors.date }}</span>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="handleCancel">
          Anuluj
        </button>
        <button type="submit" class="btn btn-success">
          {{ mode === 'add' ? 'Dodaj' : 'Zapisz' }}
        </button>
      </div>
    </form>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { meta } from '../services/api'
import type { Transaction } from '../services/api'
import Modal from './Modal.vue'

const props = defineProps<{
  modelValue: boolean
  mode: 'add' | 'edit'
  transaction?: Transaction
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'submit': [data: Omit<Transaction, 'id'>]
}>()

const isOpen = ref(props.modelValue)

const formData = ref({
  name: '',
  type: '' as 'income' | 'expense' | '',
  amount: 0,
  category: '',
  date: new Date().toISOString().slice(0, 10)
})

const errors = ref<Record<string, string>>({})

const availableCategories = computed(() => {
  if (formData.value.type === 'income') {
    return meta.categories.income
  } else if (formData.value.type === 'expense') {
    return meta.categories.expense
  }
  return []
})

watch(() => props.modelValue, (value) => {
  isOpen.value = value
  if (value) {
    if (props.mode === 'edit' && props.transaction) {
      formData.value = {
        name: props.transaction.name,
        type: props.transaction.type,
        amount: props.transaction.amount,
        category: props.transaction.category,
        date: props.transaction.date
      }
    } else {
      formData.value = {
        name: '',
        type: '',
        amount: 0,
        category: '',
        date: new Date().toISOString().slice(0, 10)
      }
    }
    errors.value = {}
  }
})

watch(isOpen, (value) => {
  emit('update:modelValue', value)
})

// Reset category when type changes
watch(() => formData.value.type, () => {
  formData.value.category = ''
})

function handleSubmit() {
  // Reset errors
  errors.value = {}

  // Validate
  if (!formData.value.name.trim()) {
    errors.value.name = 'Pole obligatoryjne'
  }
  if (!formData.value.type) {
    errors.value.type = 'Pole obligatoryjne'
  }
  if (!formData.value.amount || formData.value.amount <= 0) {
    errors.value.amount = 'Kwota musi być większa od 0'
  }
  if (!formData.value.category) {
    errors.value.category = 'Pole obligatoryjne'
  }
  if (!formData.value.date) {
    errors.value.date = 'Pole obligatoryjne'
  }

  if (Object.keys(errors.value).length > 0) {
    return
  }

  emit('submit', {
    name: formData.value.name,
    type: formData.value.type as 'income' | 'expense',
    amount: formData.value.amount,
    category: formData.value.category,
    date: formData.value.date
  })

  isOpen.value = false
}

function handleCancel() {
  isOpen.value = false
}
</script>

<style scoped>
.transaction-form {
  margin: 0;
}
</style>
