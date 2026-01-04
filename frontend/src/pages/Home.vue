<template>
  <section>
    <!-- Motivational Quote -->
    <div class="card quote-card">
      <div class="quote-icon">💡</div>
      <blockquote class="quote-text">
        "{{ currentQuote.text }}"
      </blockquote>
      <p class="quote-author">— {{ currentQuote.author }}</p>
    </div>

    <!-- Kafle miesięcznych sum -->
    <div class="grid cols-3 monthly-summary">
      <div class="kafel stat">
        <div class="stat__label">Przychody miesięczne</div>
        <div class="stat__value stat__value--income">{{ summary.incomeMonthly }} PLN</div>
      </div>
      <div class="kafel stat">
        <div class="stat__label">Wydatki miesięczne</div>
        <div class="stat__value stat__value--expense">{{ summary.expenseMonthly }} PLN</div>
      </div>
      <div class="kafel stat">
        <div class="stat__label">Bilans miesięczny</div>
        <div
          class="stat__value"
          :class="summary.balanceMonthly >= 0 ? 'stat__value--income' : 'stat__value--expense'"
        >
          {{ summary.balanceMonthly }} PLN
        </div>
      </div>
    </div>

    <!-- Ostatnie transakcje -->
    <div v-if="recent.length > 0" class="card" style="margin-top:1rem;">
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
                  {{ t.amount }} PLN
                </span>
              </td>
              <td>{{ t.category }}</td>
              <td>{{ t.date }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty state for transactions -->
    <div v-else class="card" style="margin-top:1rem;">
      <EmptyState
        icon="📊"
        title="Brak transakcji"
        message="Nie masz jeszcze żadnych transakcji. Dodaj pierwszą transakcję aby zobaczyć ją tutaj."
      />
    </div>

    <!-- Wykres: Bilans w ostatnim miesiącu -->
    <div class="card" style="margin-top:1rem;">
      <h3 style="margin:0 0 .6rem;">Bilans w ostatnim miesiącu</h3>
      <div class="chart-container">
        <div class="y-axis">
            <span>Bilans (PLN)</span>
        </div>
        <div class="chart-bars">
            <div v-for="(label, i) in charts.daily.labels" :key="label" class="bar-group-single" :title="`${label}: ${charts.daily.balance[i]} PLN`">
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
      <div class="caption" style="margin-top:2.5rem;">Oś X: Dni miesiąca • Oś Y: Wartość numeryczna w PLN</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getDashboardSummary, getRecentTransactions, getCharts } from '../services/api'
import type { DashboardSummary, Transaction, ChartsResponse } from '../services/api'
import EmptyState from '../components/EmptyState.vue'

const props = defineProps<{
  user: { id: string; [key: string]: any } | null
}>()

const businessQuotes = [
  {
    text: "Price is what you pay. Value is what you get.",
    author: "Warren Buffett"
  },
  {
    text: "Risk comes from not knowing what you're doing.",
    author: "Warren Buffett"
  },
  {
    text: "The stock market is a device for transferring money from the impatient to the patient.",
    author: "Warren Buffett"
  },
  {
    text: "When something is important enough, you do it even if the odds are not in your favor.",
    author: "Elon Musk"
  },
  {
    text: "Failure is an option here. If things are not failing, you are not innovating enough.",
    author: "Elon Musk"
  },
  {
    text: "Persistence is very important. You should not give up unless you are forced to give up.",
    author: "Elon Musk"
  },
  {
    text: "Sukces to umiejętność przejścia od porażki do porażki bez utraty entuzjazmu.",
    author: "Rafał Brzoska"
  },
  {
    text: "Nie ma rzeczy niemożliwych, są tylko rzeczy, których jeszcze nie zrobiliśmy.",
    author: "Rafał Brzoska"
  },
  {
    text: "Work smarter, not harder!",
    author: "Sknerus McKwacz"
  },
  {
    text: "Time is money, and I've got both!",
    author: "Sknerus McKwacz"
  },
  {
    text: "The way to get started is to quit talking and begin doing.",
    author: "Walt Disney"
  },
  {
    text: "Innovation distinguishes between a leader and a follower.",
    author: "Steve Jobs"
  },
  {
    text: "Your time is limited, don't waste it living someone else's life.",
    author: "Steve Jobs"
  },
  {
    text: "The only way to do great work is to love what you do.",
    author: "Steve Jobs"
  },
  {
    text: "I'm convinced that about half of what separates successful entrepreneurs from the non-successful ones is pure perseverance.",
    author: "Steve Jobs"
  },
  {
    text: "Don't be afraid to give up the good to go for the great.",
    author: "John D. Rockefeller"
  },
  {
    text: "If you don't find a way to make money while you sleep, you will work until you die.",
    author: "Warren Buffett"
  },
  {
    text: "The biggest risk is not taking any risk.",
    author: "Mark Zuckerberg"
  },
  {
    text: "Ideas are easy. Implementation is hard.",
    author: "Guy Kawasaki"
  },
  {
    text: "Business opportunities are like buses, there's always another one coming.",
    author: "Richard Branson"
  }
]

const currentQuote = ref(businessQuotes[Math.floor(Math.random() * businessQuotes.length)])

const summary = ref<DashboardSummary>({ 
  incomeDaily: 0, 
  expenseDaily: 0, 
  balanceDaily: 0,
  incomeMonthly: 0,
  expenseMonthly: 0,
  balanceMonthly: 0
})
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
  if (props.user) {
    summary.value = await getDashboardSummary(props.user.id)
    recent.value = await getRecentTransactions(props.user.id)
    charts.value = await getCharts(props.user.id)
  }
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
.quote-card {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  color: white;
  text-align: center;
  padding: 2rem;
  margin-bottom: 1rem;
  border: none;
}

.quote-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.quote-text {
  font-size: 1.2rem;
  font-style: italic;
  margin: 0 0 1rem;
  line-height: 1.6;
  font-weight: 300;
}

.quote-author {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  opacity: 0.9;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: .35rem;
}
.stat__label {
  color: var(--muted);
  font-weight: 600; /* Bolded as requested */
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
  padding-top: 20px;
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
    writing-mode: vertical-rl;
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
    .monthly-summary.grid.cols-3 {
        grid-template-columns: 1fr;
    }
    .chart-bars {
        gap: 2px;
    }
    .bar-value {
        display: none;
    }
}
</style>
