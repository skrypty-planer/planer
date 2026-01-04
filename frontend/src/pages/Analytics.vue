<template>
  <section>
    <!-- Średnie dzienne (Top) -->
    <div class="card">
      <div class="chart-header">
        <h3 style="margin:0;">Średnie dzienne: przychody i wydatki</h3>
        <div class="buttons">
            <button class="kafel" :class="{ active: averagesPeriod === 'yearly' }" @click="averagesPeriod = 'yearly'">Rok</button>
            <button class="kafel" :class="{ active: averagesPeriod === 'halfYearly' }" @click="averagesPeriod = 'halfYearly'">Pół roku</button>
            <button class="kafel" :class="{ active: averagesPeriod === 'quarterly' }" @click="averagesPeriod = 'quarterly'">Kwartał</button>
            <button class="kafel" :class="{ active: averagesPeriod === 'monthly' }" @click="averagesPeriod = 'monthly'">Miesiąc</button>
            <button class="kafel" :class="{ active: averagesPeriod === 'weekly' }" @click="averagesPeriod = 'weekly'">Tydzień</button>
        </div>
      </div>
      <div class="grid cols-2 daily-averages">
        <div class="kafel">
          <div class="caption">Średni dzienny przychód</div>
          <div class="stat__value stat__value--income">{{ currentAverages.avgDailyIncome }} PLN</div>
        </div>
        <div class="kafel">
          <div class="caption">Średni dzienny wydatek</div>
          <div class="stat__value stat__value--expense">{{ currentAverages.avgDailyExpense }} PLN</div>
        </div>
      </div>
    </div>

    <!-- Unified Balance Chart -->
    <div class="card" style="margin-top:1rem;">
      <div class="chart-header">
        <h3 style="margin:0;">Bilans</h3>
        <div class="buttons">
            <button class="kafel" :class="{ active: currentPeriod === 'yearly' }" @click="currentPeriod = 'yearly'">Rok</button>
            <button class="kafel" :class="{ active: currentPeriod === 'halfYearly' }" @click="currentPeriod = 'halfYearly'">Pół roku</button>
            <button class="kafel" :class="{ active: currentPeriod === 'quarterly' }" @click="currentPeriod = 'quarterly'">Kwartał</button>
            <button class="kafel" :class="{ active: currentPeriod === 'monthly' }" @click="currentPeriod = 'monthly'">Miesiąc</button>
            <button class="kafel" :class="{ active: currentPeriod === 'weekly' }" @click="currentPeriod = 'weekly'">Tydzień</button>
        </div>
      </div>
      
      <div class="chart-container">
         <div class="y-axis">
            <span>Bilans (PLN)</span>
        </div>
        <div class="chart-bars">
            <div v-for="(label, i) in currentChartData.labels" :key="label + i" class="bar-group-single" :title="`${label}: ${currentChartData.data[i]} PLN`">
                <div class="bar-value" :class="currentChartData.data[i] >= 0 ? 'text-income' : 'text-expense'">
                    {{ formatValue(currentChartData.data[i]) }}
                </div>
                <div 
                    class="bar" 
                    :class="currentChartData.data[i] >= 0 ? 'bar--income' : 'bar--expense'" 
                    :style="{ height: toHeight(Math.abs(currentChartData.data[i])) }"
                ></div>
                <div class="x-label" v-if="shouldShowLabel(i, currentChartData.labels.length)">{{ formatLabel(label) }}</div>
            </div>
        </div>
      </div>
      <div class="caption" style="margin-top:2.5rem;">Oś X: {{ xAxisLabel }} • Oś Y: Wartość numeryczna w PLN</div>
    </div>

    <!-- Pie Charts: Category Rankings -->
    <div class="card" style="margin-top:1rem;">
      <div class="chart-header">
        <h3 style="margin:0;">Ranking kategorii</h3>
        <div class="buttons">
            <button class="kafel" :class="{ active: piePeriod === 'yearly' }" @click="piePeriod = 'yearly'">Rok</button>
            <button class="kafel" :class="{ active: piePeriod === 'halfYearly' }" @click="piePeriod = 'halfYearly'">Pół roku</button>
            <button class="kafel" :class="{ active: piePeriod === 'quarterly' }" @click="piePeriod = 'quarterly'">Kwartał</button>
            <button class="kafel" :class="{ active: piePeriod === 'monthly' }" @click="piePeriod = 'monthly'">Miesiąc</button>
            <button class="kafel" :class="{ active: piePeriod === 'weekly' }" @click="piePeriod = 'weekly'">Tydzień</button>
        </div>
      </div>

      <div class="grid cols-2 pie-charts-grid">
        <div>
          <h4 style="text-align: center; margin: 0 0 1rem; color: var(--text);">Wydatki</h4>
          <PieChart :data="expenseCategories" />
        </div>
        <div>
          <h4 style="text-align: center; margin: 0 0 1rem; color: var(--text);">Przychody</h4>
          <PieChart :data="incomeCategories" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { getCharts, getCategoryBreakdown } from '../services/api'
import type { ChartsResponse, ChartData, CategoryBreakdown } from '../services/api'
import PieChart from '../components/PieChart.vue'

const props = defineProps<{
  user: { id: string; [key: string]: any } | null
}>()

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

const currentPeriod = ref<'yearly' | 'halfYearly' | 'quarterly' | 'monthly' | 'weekly'>('monthly')
const piePeriod = ref<'yearly' | 'halfYearly' | 'quarterly' | 'monthly' | 'weekly'>('monthly')
const averagesPeriod = ref<'yearly' | 'halfYearly' | 'quarterly' | 'monthly' | 'weekly'>('monthly')
const expenseCategories = ref<CategoryBreakdown[]>([])
const incomeCategories = ref<CategoryBreakdown[]>([])

const currentChartData = computed<ChartData>(() => {
    return charts.value.unified[currentPeriod.value]
})

const xAxisLabel = computed(() => {
  switch (currentPeriod.value) {
    case 'yearly':
    case 'halfYearly':
    case 'quarterly':
      return 'Miesiące'
    case 'monthly':
      return 'Dni miesiąca'
    case 'weekly':
      return 'Dni tygodnia'
    default:
      return 'Oś X'
  }
})

const currentAverages = computed(() => {
  if (!props.user) return { avgDailyIncome: 0, avgDailyExpense: 0 }
  
  // Calculate averages based on selected period
  const now = new Date()
  let daysInPeriod = 30
  
  switch (averagesPeriod.value) {
    case 'yearly':
      daysInPeriod = 365
      break
    case 'halfYearly':
      daysInPeriod = 183
      break
    case 'quarterly':
      daysInPeriod = 92
      break
    case 'monthly':
      daysInPeriod = 30
      break
    case 'weekly':
      daysInPeriod = 7
      break
  }
  
  // Simple calculation: divide monthly average by days
  const baseIncome = charts.value.averages.avgDailyIncome
  const baseExpense = charts.value.averages.avgDailyExpense
  
  return {
    avgDailyIncome: Math.round(baseIncome * (30 / daysInPeriod)),
    avgDailyExpense: Math.round(baseExpense * (30 / daysInPeriod))
  }
})

onMounted(async () => {
  if (props.user) {
    charts.value = await getCharts(props.user.id)
    await loadPieCharts()
  }
})

async function loadPieCharts() {
  if (!props.user) return
  expenseCategories.value = await getCategoryBreakdown(props.user.id, 'expense', piePeriod.value)
  incomeCategories.value = await getCategoryBreakdown(props.user.id, 'income', piePeriod.value)
}

// Watch pie period changes

watch(piePeriod, loadPieCharts)

function toHeight(v: number) {
  // Dynamic scaling based on max value in current dataset would be better, but fixed for now
  const max = Math.max(...currentChartData.value.data.map(Math.abs), 1000)
  const h = Math.round((v / max) * 180)
  return `${Math.max(2, Math.min(h, 180))}px`
}

function shouldShowLabel(index: number, total: number) {
    if (total <= 12) return true;
    if (total <= 31) return index % 5 === 0;
    return index % Math.ceil(total / 10) === 0;
}

function formatLabel(label: string) {
    if (label.startsWith('Month')) return label.replace('Month ', 'M');
    if (label.length > 10) return label.slice(5); // Remove year from date
    return label;
}

function formatValue(v: number) {
    return v > 0 ? `+${v}` : `${v}`
}
</script>

<style scoped>
.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .6rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.buttons button.active {
    background-color: var(--primary);
    color: white;
    border-color: var(--primary);
}

.chart-container {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding-bottom: 20px; /* Space for x-labels */
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
  display: flex;
  justify-content: space-around;
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
  flex: 1;
  margin: 0 2px;
}
.bar {
  width: 100%;
  background: #ccc;
  border-radius: 3px 3px 0 0;
  min-width: 4px;
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
    bottom: -25px;
    font-size: 0.7rem;
    color: #666;
    white-space: nowrap;
}
.bar--income { background: #c8e6c9; border: 1px solid #81c784; }
.bar--expense { background: #ffcdd2; border: 1px solid #e57373; }

.stat__value {
  font-size: 1.2rem;
  font-weight: 600;
}
.stat__value--income { color: var(--success); }
.stat__value--expense { color: var(--danger); }

.pie-charts-grid {
  gap: 2rem;
  margin-top: 1rem;
}

/* RWD */
@media (max-width: 768px) {
    .chart-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .daily-averages.grid.cols-2 {
        grid-template-columns: 1fr;
    }
    .pie-charts-grid.grid.cols-2 {
        grid-template-columns: 1fr;
    }
    .bar-value {
        display: none;
    }
}
</style>
