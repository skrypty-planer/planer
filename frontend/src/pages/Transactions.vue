<template>
  <section>
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="margin:0;">Transakcje – filtry</h3>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary" @click="exportToCSV">
            📥 Eksportuj CSV
          </button>
          <button class="btn btn-success" @click="openAddModal">
            ➕ Dodaj transakcję
          </button>
        </div>
      </div>
      <div class="grid cols-3 filters-grid">
        <div>
          <label class="caption">Data od</label>
          <input type="date" v-model="filters.dateFrom" class="form-input" style="width: 100%;" />
        </div>
        <div>
          <label class="caption">Data do</label>
          <input type="date" v-model="filters.dateTo" class="form-input" style="width: 100%;" />
        </div>
        <div>
          <label class="caption">Nazwa</label>
          <input type="text" v-model="filters.name" placeholder="np. Zakupy" class="form-input" />
        </div>
        <div>
          <label class="caption">Kwota od</label>
          <input type="number" v-model.number="filters.amountMin" placeholder="np. 10" class="form-input" />
        </div>
        <div>
          <label class="caption">Kwota do</label>
          <input type="number" v-model.number="filters.amountMax" placeholder="np. 500" class="form-input" />
        </div>
        <div>
          <label class="caption">Typ</label>
          <select v-model="filters.type" class="form-select">
            <option value="">—</option>
            <option value="income">Przychód</option>
            <option value="expense">Wydatek</option>
          </select>
        </div>
        <div>
          <label class="caption">Kategoria</label>
          <select v-model="filters.category" class="form-select">
            <option value="">—</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div style="margin-top:1rem; display: flex; gap: 0.5rem;">
        <button class="btn btn-primary" @click="applyFilters">Zastosuj</button>
        <button class="btn btn-secondary" @click="resetFilters">Wyczyść</button>
      </div>
    </div>

    <div v-if="items.length > 0" class="card" style="margin-top:1rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: .6rem;">
        <h3 style="margin:0;">Wszystkie transakcje ({{ metaState.total }})</h3>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <label class="caption" style="margin:0;">Sortowanie:</label>
          <select v-model="filters.sort" class="form-select" style="width: auto; padding: 0.4rem;">
            <option value="">Domyślne (Najnowsze)</option>
            <option value="amount-asc">Najtańsze</option>
            <option value="amount-desc">Najdroższe</option>
            <option value="date-desc">Najnowsze</option>
            <option value="date-asc">Najstarsze</option>
          </select>
        </div>
      </div>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Nazwa transakcji</th>
              <th>Typ</th>
              <th>Kwota</th>
              <th>Kategoria</th>
              <th>Data</th>
              <th style="width: 120px;">Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in items" :key="t.id">
              <td>{{ t.name }}</td>
              <td>{{ t.type === 'income' ? 'Przychód' : 'Wydatek' }}</td>
              <td>
                <span class="badge" :class="t.type === 'income' ? 'badge--income' : 'badge--expense'">
                  {{ t.amount }} zł
                </span>
              </td>
              <td>{{ t.category }}</td>
              <td>{{ t.date }}</td>
              <td>
                <button class="btn btn-secondary btn-icon" @click="openEditModal(t)" title="Edytuj">
                  ✏️
                </button>
                <button class="btn btn-danger btn-icon" @click="openDeleteModal(t)" title="Usuń" style="margin-left: 0.25rem;">
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="card" style="margin-top:1rem;">
      <EmptyState
        icon="📊"
        title="Brak transakcji"
        message="Nie znaleziono transakcji spełniających kryteria lub nie masz jeszcze żadnych transakcji."
      >
        <template #action>
          <button class="btn btn-success" @click="openAddModal">
            Dodaj pierwszą transakcję
          </button>
        </template>
      </EmptyState>
    </div>

    <!-- Transaction Form Modal -->
    <TransactionFormModal
      v-model="showTransactionModal"
      :mode="modalMode"
      :transaction="editingTransaction"
      @submit="handleTransactionSubmit"
    />

    <!-- Delete Confirmation Modal -->
    <Modal
      v-model="showDeleteModal"
      title="Usuń transakcję"
      :message="`Czy na pewno chcesz usunąć transakcję: ${deletingTransaction?.name}?`"
      :show-cancel="true"
      :show-confirm="true"
      cancel-text="Anuluj"
      confirm-text="Usuń"
      confirm-class="btn-danger"
      @confirm="handleDelete"
    />
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { getAllTransactions, meta, addTransaction, updateTransaction, deleteTransaction } from '../services/api'
import type { Transaction } from '../services/api'
import EmptyState from '../components/EmptyState.vue'
import TransactionFormModal from '../components/TransactionFormModal.vue'
import Modal from '../components/Modal.vue'

const props = defineProps<{
  user: { id: string; [key: string]: any } | null
}>()

const filters = reactive({
  dateFrom: '',
  dateTo: '',
  name: '',
  amountMin: undefined as number | undefined,
  amountMax: undefined as number | undefined,
  category: '',
  type: '' as '' | 'income' | 'expense',
  sort: '' as '' | 'amount-asc' | 'amount-desc' | 'date-asc' | 'date-desc'
})

const items = ref<Transaction[]>([])
const metaState = ref({ total: 0 })
const categories = ref<string[]>([])
const showTransactionModal = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const editingTransaction = ref<Transaction | undefined>()
const showDeleteModal = ref(false)
const deletingTransaction = ref<Transaction | null>(null)

function loadCategoriesByType() {
  if (filters.type === 'income') {
    categories.value = meta.categories.income
  } else if (filters.type === 'expense') {
    categories.value = meta.categories.expense
  } else {
    categories.value = [...meta.categories.income, ...meta.categories.expense]
  }
}

async function load() {
  if (!props.user) return
  const { items: list, meta: m } = await getAllTransactions(props.user.id, { ...filters })
  items.value = list
  metaState.value = m
}

function applyFilters() {
  load()
}

function resetFilters() {
  filters.dateFrom = ''
  filters.dateTo = ''
  filters.name = ''
  filters.amountMin = undefined
  filters.amountMax = undefined
  filters.category = ''
  filters.type = ''
  // Keep sort selection - don't reset it
  loadCategoriesByType()
  load()
}

function exportToCSV() {
  if (items.value.length === 0) return

  const headers = ['ID', 'Nazwa', 'Typ', 'Kwota', 'Kategoria', 'Data']
  const rows = items.value.map(t => [
    t.id,
    t.name,
    t.type,
    t.amount,
    t.category,
    t.date
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', 'transakcje.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function openAddModal() {
  modalMode.value = 'add'
  editingTransaction.value = undefined
  showTransactionModal.value = true
}

function openEditModal(transaction: Transaction) {
  modalMode.value = 'edit'
  editingTransaction.value = transaction
  showTransactionModal.value = true
}

function openDeleteModal(transaction: Transaction) {
  deletingTransaction.value = transaction
  showDeleteModal.value = true
}

async function handleTransactionSubmit(data: Omit<Transaction, 'id'>) {
  if (!props.user) return
  if (modalMode.value === 'add') {
    await addTransaction(props.user.id, data)
  } else if (editingTransaction.value) {
    await updateTransaction(props.user.id, editingTransaction.value.id, data)
  }
  await load()
}

async function handleDelete() {
  if (!props.user) return
  if (deletingTransaction.value) {
    await deleteTransaction(props.user.id, deletingTransaction.value.id)
    showDeleteModal.value = false
    deletingTransaction.value = null
    await load()
  }
}

watch(() => filters.type, () => {
  loadCategoriesByType()
})

// Watch for sort changes to apply immediately
watch(() => filters.sort, () => {
  load()
})

onMounted(async () => {
  if (props.user) {
    loadCategoriesByType()
    await load()
  }
})
</script>

<style scoped>
/* Lokalny test styli */
h3 {
  color: var(--text);
}

.table-container {
    overflow-x: auto;
}

/* RWD */
@media (max-width: 768px) {
    .filters-grid.grid.cols-3 {
        grid-template-columns: 1fr;
    }
}
</style>
