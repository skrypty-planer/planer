<template>
  <section>
    <div class="card">
      <h3 style="margin:0 0 .6rem;">Transakcje – filtry</h3>
      <div class="grid cols-3 filters-grid">
        <div>
          <label class="caption">Data od</label>
          <input type="date" v-model="filters.dateFrom" class="kafel" />
        </div>
        <div>
          <label class="caption">Data do</label>
          <input type="date" v-model="filters.dateTo" class="kafel" />
        </div>
        <div>
          <label class="caption">Nazwa</label>
          <input type="text" v-model="filters.name" placeholder="np. Wydatek: Jedzenie" class="kafel" />
        </div>
        <div>
          <label class="caption">Kwota (dokładna)</label>
          <input type="number" v-model.number="filters.amount" placeholder="np. 120" class="kafel" />
        </div>
        <div>
          <label class="caption">Typ</label>
          <select v-model="filters.type" class="kafel">
            <option value="">—</option>
            <option value="income">Przychód</option>
            <option value="expense">Wydatek</option>
          </select>
        </div>
        <div>
          <label class="caption">Kategoria</label>
          <select v-model="filters.category" class="kafel">
            <option value="">—</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div style="margin-top:.6rem;">
        <button class="kafel" @click="applyFilters">Zastosuj</button>
        <button class="kafel" style="margin-left:.5rem;" @click="resetFilters">Wyczyść</button>
      </div>
    </div>

    <div class="card" style="margin-top:1rem;">
      <h3 style="margin:0 0 .6rem;">Wszystkie transakcje ({{ metaState.total }})</h3>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Nazwa transakcji</th>
              <th>Typ</th>
              <th>Kwota</th>
              <th>Kategoria</th>
              <th>Data</th>
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
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { getAllTransactions, meta } from '../services/api'
import type { Transaction } from '../services/api'

const props = defineProps<{
  user: { id: string; [key: string]: any }
}>()

const filters = reactive({
  dateFrom: '',
  dateTo: '',
  name: '',
  amount: undefined as number | undefined,
  category: '',
  type: '' as '' | 'income' | 'expense'
})

const items = ref<Transaction[]>([])
const metaState = ref({ total: 0 })
const categories = ref<string[]>([])

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
  filters.amount = undefined
  filters.category = ''
  filters.type = ''
  loadCategoriesByType()
  load()
}

watch(() => filters.type, () => {
  loadCategoriesByType()
})

onMounted(async () => {
  loadCategoriesByType()
  await load()
})
</script>

<style scoped>
/* Lokalny test styli */
h3 {
  color: #333;
}
input.kafel, select.kafel, button.kafel {
  padding: .5rem .6rem;
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
