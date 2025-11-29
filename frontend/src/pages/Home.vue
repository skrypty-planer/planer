<template>
  <section>
    <!-- Kafle dziennych sum -->
    <div class="grid cols-3 daily-summary">
      <div class="kafel stat">
        <div class="stat__label">Przychody dzienne</div>
        <div class="stat__value stat__value--income">{{ summary.incomeDaily }} zł</div>
      </div>
      <div class="kafel stat">
        <div class="stat__label">Wydatki dzienne</div>
        <div class="stat__value stat__value--expense">{{ summary.expenseDaily }} zł</div>
      </div>
      <div class="kafel stat">
        <div class="stat__label">Bilans dzienny</div>
        <div
          class="stat__value"
          :class="summary.balanceDaily >= 0 ? 'stat__value--income' : 'stat__value--expense'"
        >
          {{ summary.balanceDaily }} zł
        </div>
      </div>
    </div>

    <!-- Ostatnie transakcje -->
    <div class="card" style="margin-top:1rem;">
      <h3 style="margin:0 0 .6rem;">Ostatnie transakcje</h3>
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
            <tr v-for="t in recent" :key="t.id">
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

    <!-- Wykres: Bilans w ostatnim miesiącu -->
    <div class="card" style="margin-top:1rem;">
      <h3 style="margin:0 0 .6rem;">Bilans w ostatnim miesiącu</h3>
      <div class="chart-container">
        <div class="y-axis">
            <span>Bilans (zł)</span>
        </div>
        <div class="chart-bars">
            <div v-for="(label, i) in charts.daily.labels" :key="label" class="bar-group-single" :title="`${label}: ${charts.daily.balance[i]} zł`">
            <div class="bar-value" :class="charts.daily.balance[i] >= 0 ? 'text-income' : 'text-expense'">
                {{ formatValue(charts.daily.balance[i]) }}
            </div>
            <div 
                class="bar" 
                :class="charts.daily.balance[i] >= 0 ? 'bar--income' : 'bar--expense'" 
                :style="{ height: toHeight(Math.abs(charts.daily.balance[i])) }"
            ></div>
            <div class="x-label" v-if="i % 5 === 0">{{ label.slice(5) }}</div>
            </div>
        </div>
      </div>
      <div class="caption" style="margin-top:2.5rem;">Oś X: Dni miesiąca • Oś Y: Wartość numeryczna w zł</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getDashboardSummary, getRecentTransactions, getCharts } from '../services/api'
import type { DashboardSummary, Transaction, ChartsResponse } from '../services/api'

const props = defineProps<{
  user: { id: string; [key: string]: any }
}>()

const summary = ref<DashboardSummary>({ incomeDaily: 0, expenseDaily: 0, balanceDaily: 0 })
const recent = ref<Transaction[]>([])
const charts = ref<ChartsResponse>({ 
    daily: { labels: [], income: [], expense: [], balance: [] },
    weekly: { labels: [], balance: [] },
    monthly: { labels: [], balance: [] },
    unified: {
        yearly: { labels: [], data: [] },
        halfYearly: { labels: [], data: [] },
        quarterly: { labels: [], data: [] },
        monthly: { labels: [], data: [] },
        weekly: { labels: [], data: [] },
    },
    averages: { avgDailyIncome: 0, avgDailyExpense: 0 },
    ranking: []
})

onMounted(async () => {
  summary.value = await getDashboardSummary(props.user.id)
  recent.value = await getRecentTransactions(props.user.id)
  charts.value = await getCharts(props.user.id)
})

function toHeight(v: number) {
  // prosty skaler słupków – maks 1000
  const max = 1000 
  const h = Math.round((v / max) * 180) // Reduced max height slightly to fit labels
  return `${Math.max(2, Math.min(h, 180))}px`
}

function formatValue(v: number) {
    return v > 0 ? `+${v}` : `${v}`
}
</script>

<style scoped>
.stat {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: .35rem;
}
.stat__label {
  color: var(--muted);
}
.stat__value {
  font-size: 1.4rem;
  font-weight: 600;
}
.stat__value--income { color: var(--success); }
.stat__value--expense { color: var(--danger); }

.chart-container {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding-bottom: 10px;
}

.y-axis {
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    text-align: center;
    font-size: 0.8rem;
    color: #666;
    height: 220px;
}

.chart-bars {
  display: grid;
  grid-template-columns: repeat(30, 1fr);
  gap: 4px;
  align-items: end;
  height: 220px;
  width: 100%;
  border-bottom: 1px solid #eee;
  border-left: 1px solid #eee;
  padding-top: 20px; /* Space for top values */
}
.bar-group-single {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
  position: relative;
}
.bar {
  width: 100%;
  background: #ccc;
  border-radius: 3px 3px 0 0;
}
.bar-value {
    font-size: 0.6rem;
    margin-bottom: 2px;
    writing-mode: vertical-rl; /* Vertical text for values to fit */
    transform: rotate(180deg);
}
.text-income { color: var(--success); }
.text-expense { color: var(--danger); }

.x-label {
    position: absolute;
    bottom: -20px;
    font-size: 0.7rem;
    color: #666;
    white-space: nowrap;
}
.bar--income { background: #c8e6c9; border: 1px solid #81c784; }
.bar--expense { background: #ffcdd2; border: 1px solid #e57373; }

.table-container {
    overflow-x: auto;
}

/* RWD */
@media (max-width: 768px) {
    .daily-summary.grid.cols-3 {
        grid-template-columns: 1fr;
    }
    .chart-bars {
        gap: 2px;
    }
    .bar-value {
        display: none; /* Hide values on very small screens if too crowded, or keep if critical */
    }
}
</style>
